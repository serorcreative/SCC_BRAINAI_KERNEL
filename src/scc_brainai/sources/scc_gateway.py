"""Passerelle SCC — accès unifié aux composants existants (réutilisation stricte).

BrainAI ne relit ni ne réimplémente rien : il **coordonne** via les interfaces
publiques déjà livrées —

* **API (08)** : ``SccApi.dispatch`` (graphe, catalogues, système, readiness) ;
* **Runtime (07)** : ``RuntimeEngine`` + ``SupervisorPort`` (exécution gouvernée) ;
* **Control Plane (09)** : ``ControlPlane`` (santé, observabilité).

Les trois sont localisés dynamiquement (ajout de leur ``src/`` à ``sys.path``),
jamais modifiés. Toute exécution Runtime est **déterministe** (horloge injectée).
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from scc_brainai.core.config import BrainAIConfig
from scc_brainai.core.errors import SourceUnavailable


class SccGateway:
    def __init__(self, config: BrainAIConfig):
        self._config = config
        self._api = None
        self._rt = None
        self._cp_cls = None

    # -- bootstrap ------------------------------------------------------- #
    @staticmethod
    def _add_path(src: Path, label: str) -> None:
        if not src.exists():
            raise SourceUnavailable(f"{label} introuvable : {src}")
        if str(src) not in sys.path:
            sys.path.insert(0, str(src))

    def _api_obj(self):
        if self._api is None:
            self._add_path(self._config.api_src, "API SCC")
            try:
                self._api = importlib.import_module("scc_api").SccApi()
            except ImportError as exc:  # pragma: no cover
                raise SourceUnavailable(f"Import API impossible : {exc}") from exc
        return self._api

    def _runtime_mod(self):
        if self._rt is None:
            self._add_path(self._config.runtime_src, "Runtime SCC")
            try:
                self._rt = importlib.import_module("scc_runtime")
            except ImportError as exc:  # pragma: no cover
                raise SourceUnavailable(f"Import Runtime impossible : {exc}") from exc
        return self._rt

    def _control_plane_cls(self):
        if self._cp_cls is None:
            self._add_path(self._config.control_plane_src, "Control Plane SCC")
            try:
                self._cp_cls = importlib.import_module("scc_control_plane").ControlPlane
            except ImportError as exc:  # pragma: no cover
                raise SourceUnavailable(f"Import Control Plane impossible : {exc}") from exc
        return self._cp_cls

    def available(self) -> Dict[str, bool]:
        out = {}
        for label, fn in (("api", self._api_obj), ("runtime", self._runtime_mod),
                          ("control_plane", self._control_plane_cls)):
            try:
                fn(); out[label] = True
            except SourceUnavailable:
                out[label] = False
        return out

    # -- API (lecture) --------------------------------------------------- #
    def api(self, operation: str, params: Optional[Dict[str, Any]] = None) -> Any:
        env = self._api_obj().dispatch(operation, params or {}).to_dict()
        if not env.get("ok"):
            raise SourceUnavailable(f"API '{operation}' a échoué : {env.get('error')}")
        return env.get("data")

    def system_status(self) -> Dict[str, Any]:
        return self.api("system.status")

    def readiness(self) -> Dict[str, Any]:
        return self.api("system.readiness")

    def graph_summary(self) -> Dict[str, Any]:
        return self.api("graph.summary")

    def graph_search(self, type: Optional[str] = None, query: str = "", limit: int = 25) -> List[dict]:
        return self.api("graph.search", {"type": type, "query": query, "limit": limit})

    def graph_neighbors(self, node_id: str, direction: str = "any",
                        relation: Optional[str] = None) -> Dict[str, Any]:
        return self.api("graph.neighbors", {"id": node_id, "direction": direction, "relation": relation})

    def agents(self) -> List[dict]:
        return self.api("catalog.agents")

    def governing_doctrines(self, node_id: str) -> List[str]:
        """Doctrines gouvernant un nœud (relation `governs` du méta-modèle)."""
        try:
            nb = self.graph_neighbors(node_id, direction="in", relation="governs")
        except SourceUnavailable:
            return []
        return sorted({n["node"] for n in nb.get("neighbors", []) if n["node"].startswith("SCC-DOC-")})

    def referencing_adrs(self, node_id: str) -> List[str]:
        """ADR référençant un nœud (relation `references` depuis un ADR)."""
        try:
            nb = self.graph_neighbors(node_id, direction="in", relation="references")
        except SourceUnavailable:
            return []
        return sorted({n["node"] for n in nb.get("neighbors", []) if n["node"].startswith("ADR-")})

    # -- Control Plane (observabilité) ---------------------------------- #
    def control_plane(self):
        cls = self._control_plane_cls()
        return cls()

    def health(self) -> Dict[str, Any]:
        return self.control_plane().health()

    # -- Runtime (exécution gouvernée, déterministe) -------------------- #
    def run_governed_job(self, kind: str, params: Dict[str, Any], supervisor,
                         actor: str, autonomy: str) -> Dict[str, Any]:
        """Exécute un job via le Runtime sous un superviseur BrainAI (déterministe)."""
        rt = self._runtime_mod()
        from scc_runtime.core.clock import FixedClock, SequentialFactory

        engine = rt.RuntimeEngine(
            clock=FixedClock(self._config.as_of),
            id_factory=SequentialFactory(),
            supervisor=supervisor,
        )
        events: List[dict] = []
        engine.events.subscribe(lambda e: events.append(e.to_dict()))
        engine.boot()
        session = engine.open_session(actor=actor, autonomy=rt.AutonomyLevel(autonomy),
                                      label="BrainAI kernel")
        job = engine.submit(session.id, kind, params)
        approved = False
        if job.status.value == "blocked":
            engine.approve(job.id, approver="brainai-human")
            approved = True
        engine.run_all()
        record = {
            "job_id": job.id, "kind": kind, "status": job.status.value,
            "trust": job.trust.value, "human_approval_required": approved,
            "session": session.id, "result": job.result, "error": job.error,
            "events": len(events),
            "events_by_type": _hist(events),
        }
        engine.shutdown()
        return record

    def job_kinds(self):
        rt = self._runtime_mod()
        return rt.JobKind


def _hist(events: List[dict]) -> Dict[str, int]:
    h: Dict[str, int] = {}
    for e in events:
        h[e["type"]] = h.get(e["type"], 0) + 1
    return dict(sorted(h.items()))


__all__ = ["SccGateway"]
