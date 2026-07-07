"""Orchestration de l'exécution des Agents et consolidation.

Chaque étape du plan est exécutée par son agent : les agents cognitifs supervisent
un **job Runtime gouverné** (chaîne des moteurs ou diagnostic), les agents de
gouvernance consultent doctrines/ADR (graphe), les agents d'inspection lisent le
Control Plane. Tout est **déterministe** et n'utilise que des interfaces publiques.
"""

from __future__ import annotations

import shutil
from typing import Any, Dict, List

from scc_brainai.core.model import Contribution, Intent, Plan, Request
from scc_brainai.sources.scc_gateway import SccGateway
from scc_brainai.supervisor import KernelSupervisor

# Agent cognitif → étage de la chaîne (pour distribuer le résultat de la passe).
_AGENT_STAGE = {
    "SCC-AGENT-0006": "ingestion", "SCC-AGENT-0007": "extraction",
    "SCC-AGENT-0008": "memory", "SCC-AGENT-0009": "knowledge",
    "SCC-AGENT-0010": "reasoning",
}


class Orchestrator:
    def __init__(self, gateway: SccGateway, config, provider):
        self._gw = gateway
        self._config = config
        self._provider = provider

    def run(self, plan: Plan, request: Request, context: Dict[str, Any],
            supervisor: KernelSupervisor) -> Dict[str, Any]:
        runtime_record = self._run_governed_job(plan, request, supervisor)

        contributions: List[Contribution] = []
        for step in plan.steps:
            findings = self._execute(step, context, runtime_record)
            contributions.append(Contribution(
                step_id=step.id, agent=step.agent, action=step.action,
                status="ok", findings=findings, provider=self._provider.name,
            ))

        governance = self._consolidate_governance(plan, contributions)
        return {
            "runtime": runtime_record,
            "contributions": [c.to_dict() for c in contributions],
            "governance": governance,
            "supervisor": supervisor.summary(),
        }

    # -- job Runtime gouverné ------------------------------------------- #
    def _run_governed_job(self, plan: Plan, request: Request,
                          supervisor: KernelSupervisor) -> Dict[str, Any]:
        kinds = self._gw.job_kinds()
        deep = bool(request.options.get("deep")) and plan.intent == Intent.COGNITION.value
        if deep:
            kind = kinds.BRAIN_PASS
            # Répertoire de travail propre à chaque passe : une passe cognitive part
            # toujours d'un état vierge (déterminisme ; pas de réingestion cumulée).
            workdir = self._config.runs_dir / "brain_pass"
            if workdir.exists():
                shutil.rmtree(workdir, ignore_errors=True)
            params = {"query": request.query, "run_id": "brainai_pass", "workdir": str(workdir)}
        else:
            kind = kinds.ECHO
            params = {"message": f"BrainAI orchestration — intent={plan.intent}"}
        try:
            return self._gw.run_governed_job(
                kind, params, supervisor,
                actor=request.actor, autonomy=request.autonomy)
        except Exception as exc:  # noqa: BLE001 - Runtime dégradé, tracé
            return {"status": "unavailable", "error": str(exc), "kind": kind}

    # -- exécution d'une étape ------------------------------------------ #
    def _execute(self, step, context: Dict[str, Any], runtime_record: Dict[str, Any]) -> Dict[str, Any]:
        action = step.action
        if action == "map_architecture":
            g = context.get("graph", {}).get("counts", {})
            adrs = [a["id"] for a in self._safe_search("ADR", limit=8)][:5]
            return {"graph": {"nodes": g.get("nodes"), "edges": g.get("edges")}, "adrs": adrs}

        if action == "consult_governance":
            return {"doctrines": step.doctrines,
                    "adrs": self._gw_safe(lambda: self._gw.referencing_adrs(step.agent))}

        if action == "check_foundation":
            found = [d["id"] for d in self._safe_search("Doctrine", query="fondation", limit=5)]
            return {"foundation_doctrines": sorted(found), "doctrines": step.doctrines}

        if action == "cognitive_stage":
            stage = _AGENT_STAGE.get(step.agent, "")
            result = runtime_record.get("result", {})
            summary = (result.get("stage_summary") or {}).get(stage)
            if summary is not None:
                return {"stage": stage, "stage_summary": {stage: summary}}
            return {"stage": stage,
                    "note": "passe cognitive complète disponible en mode deep",
                    "runtime_job": runtime_record.get("job_id")}

        if action == "inspect_health":
            h = context.get("health", {})
            return {"health": h.get("overall"), "domains": len(h.get("domains", []))}

        if action == "observe_supervision":
            return {"runtime_job": runtime_record.get("job_id"),
                    "runtime_status": runtime_record.get("status"),
                    "events_by_type": runtime_record.get("events_by_type", {})}

        return {"note": f"action non spécialisée : {action}"}

    # -- consolidation gouvernance -------------------------------------- #
    def _consolidate_governance(self, plan: Plan, contributions: List[Contribution]) -> Dict[str, Any]:
        doctrines = set()
        adrs = set()
        for step in plan.steps:
            doctrines.update(step.doctrines)
        for c in contributions:
            adrs.update(c.findings.get("adrs", []) or [])
            doctrines.update(c.findings.get("foundation_doctrines", []) or [])
        return {"doctrines": sorted(doctrines), "adrs": sorted(adrs),
                "count_doctrines": len(doctrines), "count_adrs": len(adrs)}

    # -- helpers -------------------------------------------------------- #
    def _safe_search(self, type_: str, query: str = "", limit: int = 10):
        try:
            return self._gw.graph_search(type=type_, query=query, limit=limit)
        except Exception:  # noqa: BLE001
            return []

    def _gw_safe(self, fn):
        try:
            return fn()
        except Exception:  # noqa: BLE001
            return []


__all__ = ["Orchestrator"]
