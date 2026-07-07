"""BrainAIKernel — noyau officiel : le chef d'orchestre cognitif de SCC.

BrainAI **coordonne** les composants existants sans en remplacer aucun. Pipeline
déterministe d'une demande à une réponse structurée :

    demande → intention → contexte → agents → doctrines/ADR → plan
            → orchestration (Runtime gouverné) → consolidation → réponse

Invariants : aucun moteur/Runtime/API/Control Plane modifié (interfaces publiques
uniquement) ; **aucune IA obligatoire** (cognition déterministe par défaut, IA
optionnelles et branchables) ; aucun réseau ; stdlib pur ; déterminisme complet.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from scc_brainai.agent_selector import select_agents
from scc_brainai.context_builder import build_context
from scc_brainai.core.config import BrainAIConfig, load_config
from scc_brainai.core.model import Intent, Request
from scc_brainai.orchestrator import Orchestrator
from scc_brainai.planner import build_plan
from scc_brainai.providers.registry import ProviderRegistry
from scc_brainai.sources.scc_gateway import SccGateway
from scc_brainai.supervisor import KernelSupervisor

# Classificateur d'intention déterministe (mots-clés → intention).
_INTENT_KEYWORDS = [
    (Intent.GOVERNANCE, ["doctrine", "gouvernance", "adr", "décision", "decision", "règle", "regle", "conformité"]),
    (Intent.INSPECT, ["état", "etat", "status", "santé", "sante", "health", "supervis", "alerte", "readiness", "diagnostic"]),
    (Intent.GRAPH, ["graphe", "graph", "nœud", "noeud", "relation", "chemin", "voisin", "structure"]),
    (Intent.COGNITION, ["raisonn", "connaissance", "analyse", "comprendre", "architecture", "question", "pourquoi", "explique"]),
]


def classify_intent(query: str, forced: Optional[str] = None) -> str:
    if forced:
        try:
            return Intent(forced).value
        except ValueError:
            pass
    q = (query or "").lower()
    for intent, keywords in _INTENT_KEYWORDS:
        if any(k in q for k in keywords):
            return intent.value
    return Intent.GENERAL.value


class BrainAIKernel:
    def __init__(self, config: Optional[BrainAIConfig] = None,
                 providers: Optional[ProviderRegistry] = None):
        self.config = config or load_config()
        self.gateway = SccGateway(self.config)
        self.providers = providers or ProviderRegistry()

    # ================================================================== #
    # Point d'entrée principal
    # ================================================================== #
    def handle(self, query, **kwargs) -> Dict[str, Any]:
        """Traite une demande de bout en bout et renvoie une réponse structurée."""
        request = self._as_request(query, kwargs)
        provider = self.providers.select(
            kwargs.get("provider_order") or self.config.provider_order)

        # 1–3. Intention + contexte d'exécution (API, graphe, Control Plane).
        intent = classify_intent(request.query, request.intent)
        context = build_context(request, self.gateway, self.config.as_of)

        # 4–5. Sélection des agents + consultation doctrines/ADR (dans le plan).
        agents = select_agents(intent, self.gateway)

        # 6. Plan d'exécution.
        plan = build_plan(intent, request.query, agents, self.gateway, provider)

        # 7. Orchestration (job Runtime gouverné + contributions).
        supervisor = KernelSupervisor(provider=provider)
        orchestrator = Orchestrator(self.gateway, self.config, provider)
        execution = orchestrator.run(plan, request, context, supervisor)

        # 8. Consolidation + synthèse (déterministe, augmentable par une IA).
        synthesis = provider.assist_synthesis(
            request.query, execution["contributions"], context) or ""

        # 9. Réponse structurée.
        return self._build_response(request, intent, context, agents, plan,
                                    execution, synthesis, provider)

    # ================================================================== #
    # Introspection
    # ================================================================== #
    def status(self) -> Dict[str, Any]:
        return {
            "version": _version(),
            "as_of": self.config.as_of,
            "sources": self.gateway.available(),
            "providers": self.providers.to_dict(),
        }

    def self_check(self) -> Dict[str, Any]:
        srcs = self.gateway.available()
        checks = [
            {"label": "api_source", "passed": srcs.get("api", False)},
            {"label": "runtime_source", "passed": srcs.get("runtime", False)},
            {"label": "control_plane_source", "passed": srcs.get("control_plane", False)},
            {"label": "deterministic_provider",
             "passed": "deterministic" in self.providers.available()},
            {"label": "works_without_external_ai",
             "passed": self.providers.select(["deterministic"]).name == "deterministic"},
            {"label": "no_llm_no_network", "passed": True},
        ]
        return {"title": "BrainAI kernel — auto-vérification",
                "ok": all(c["passed"] for c in checks),
                "checks": checks}

    # ================================================================== #
    # Helpers
    # ================================================================== #
    def _as_request(self, query, kwargs: Dict[str, Any]) -> Request:
        if isinstance(query, Request):
            return query
        return Request(
            query=str(query),
            actor=kwargs.get("actor", self.config.default_actor),
            autonomy=kwargs.get("autonomy", self.config.default_autonomy),
            intent=kwargs.get("intent"),
            options=dict(kwargs.get("options", {})),
        )

    def _build_response(self, request, intent, context, agents, plan,
                        execution, synthesis, provider) -> Dict[str, Any]:
        return {
            "ok": True,
            "as_of": self.config.as_of,
            "request": request.to_dict(),
            "intent": intent,
            "context": {
                "system": {"components_present": context.get("system", {}).get("components_present"),
                           "graph": context.get("system", {}).get("graph")},
                "readiness": context.get("readiness", {}).get("verdict"),
                "health": context.get("health", {}).get("overall"),
                "sources": context.get("sources", {}),
                "notes": context.get("notes", []),
            },
            "agents": [a.to_dict() for a in agents],
            "plan": plan.to_dict(),
            "governance": execution["governance"],
            "runtime": execution["runtime"],
            "supervisor": execution["supervisor"],
            "contributions": execution["contributions"],
            "synthesis": synthesis,
            "provider": {"selected": provider.name,
                         "available": self.providers.available()},
        }


def _version() -> str:
    from scc_brainai import __version__
    return __version__


__all__ = ["BrainAIKernel", "classify_intent"]
