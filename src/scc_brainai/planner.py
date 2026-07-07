"""Construction du plan d'exécution.

À partir de l'intention et des agents sélectionnés, le planificateur construit un
plan déterministe : une étape par agent, dotée d'une **action** (dérivée du rôle)
et des **doctrines** qui la gouvernent (lues dans le graphe, relation `governs`).
Un fournisseur d'intelligence peut *augmenter* le raisonnement du plan (indices),
sans jamais en être requis.
"""

from __future__ import annotations

from typing import Dict, List

from scc_brainai.core.model import AgentRef, Intent, Plan, PlanStep
from scc_brainai.sources.scc_gateway import SccGateway

# Rôle d'agent → action d'exécution (déterministe).
_AGENT_ACTION = {
    "SCC-AGENT-0001": "map_architecture",
    "SCC-AGENT-0002": "consult_governance",
    "SCC-AGENT-0003": "check_foundation",
    "SCC-AGENT-0006": "cognitive_stage",
    "SCC-AGENT-0007": "cognitive_stage",
    "SCC-AGENT-0008": "cognitive_stage",
    "SCC-AGENT-0009": "cognitive_stage",
    "SCC-AGENT-0010": "cognitive_stage",
    "SCC-AGENT-0015": "inspect_health",
    "SCC-AGENT-0016": "inspect_health",
    "SCC-AGENT-0020": "observe_supervision",
}

_ACTION_DESC = {
    "map_architecture": "Cartographier la structure (graphe) et les décisions pertinentes.",
    "consult_governance": "Consulter les doctrines et ADR gouvernant la demande.",
    "check_foundation": "Vérifier les invariants de la Fondation.",
    "cognitive_stage": "Superviser un étage de la chaîne cognitive du Runtime.",
    "inspect_health": "Relever la santé et les alertes via le Control Plane.",
    "observe_supervision": "Superviser l'exécution et consolider (rôle incarné par BrainAI).",
}


def build_plan(intent: str, query: str, agents: List[AgentRef], gateway: SccGateway,
               provider) -> Plan:
    steps: List[PlanStep] = []
    for i, agent in enumerate(agents, start=1):
        action = _AGENT_ACTION.get(agent.id, "inspect_health")
        doctrines = _safe_doctrines(gateway, agent.id)
        steps.append(PlanStep(
            id=f"step-{i:02d}",
            agent=agent.id,
            action=action,
            description=_ACTION_DESC.get(action, action),
            doctrines=doctrines,
        ))

    hints = []
    if provider is not None and provider.available():
        hints = provider.assist_plan(intent, query, {}) or []
    rationale = " ".join(hints) if hints else \
        f"Plan déterministe pour l'intention « {intent} » : {len(steps)} étape(s)."
    return Plan(intent=intent, rationale=rationale, steps=steps)


def _safe_doctrines(gateway: SccGateway, agent_id: str) -> List[str]:
    try:
        return gateway.governing_doctrines(agent_id)
    except Exception:  # noqa: BLE001
        return []


__all__ = ["build_plan"]
