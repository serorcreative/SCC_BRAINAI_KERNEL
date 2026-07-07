"""Sélection des Agents concernés — déterministe, ancrée sur le catalogue réel.

BrainAI ne crée pas d'agents : il **sélectionne** des rôles existants
(`SCC-AGENT-NNNN`) selon l'intention, et les enrichit de leurs attributs réels
(autonomie, confiance) lus via l'API. BrainAI *incarne* systématiquement le
Superviseur (SCC-AGENT-0020, méta-modèle).
"""

from __future__ import annotations

from typing import Dict, List

from scc_brainai.core.model import AgentRef, Intent
from scc_brainai.sources.scc_gateway import SccGateway

SUPERVISOR = "SCC-AGENT-0020"

# Intention → rôles pertinents (le Superviseur est toujours ajouté).
_INTENT_AGENTS: Dict[str, List[str]] = {
    Intent.COGNITION.value: ["SCC-AGENT-0006", "SCC-AGENT-0007", "SCC-AGENT-0008",
                             "SCC-AGENT-0009", "SCC-AGENT-0010", "SCC-AGENT-0001"],
    Intent.GOVERNANCE.value: ["SCC-AGENT-0002", "SCC-AGENT-0003", "SCC-AGENT-0001"],
    Intent.GRAPH.value: ["SCC-AGENT-0001", "SCC-AGENT-0009"],
    Intent.INSPECT.value: ["SCC-AGENT-0015", "SCC-AGENT-0016", "SCC-AGENT-0001"],
    Intent.GENERAL.value: ["SCC-AGENT-0001", "SCC-AGENT-0002"],
}

_REASONS = {
    "SCC-AGENT-0001": "cartographie et arbitrage d'architecture",
    "SCC-AGENT-0002": "consultation de la gouvernance et des doctrines",
    "SCC-AGENT-0003": "vérification des invariants de la Fondation",
    "SCC-AGENT-0006": "étage d'ingestion de la chaîne cognitive",
    "SCC-AGENT-0007": "étage d'extraction",
    "SCC-AGENT-0008": "étage de mémoire",
    "SCC-AGENT-0009": "étage de connaissance / graphe",
    "SCC-AGENT-0010": "étage de raisonnement",
    "SCC-AGENT-0015": "contrôle qualité",
    "SCC-AGENT-0016": "contrôle de sécurité",
    SUPERVISOR: "supervision cognitive (incarnée par BrainAI)",
}


def select_agents(intent: str, gateway: SccGateway) -> List[AgentRef]:
    wanted = list(_INTENT_AGENTS.get(intent, _INTENT_AGENTS[Intent.GENERAL.value]))
    if SUPERVISOR not in wanted:
        wanted.append(SUPERVISOR)

    # Métadonnées réelles depuis le catalogue (API).
    try:
        catalog = {a["id"]: a for a in gateway.agents()}
    except Exception:  # noqa: BLE001
        catalog = {}

    refs: List[AgentRef] = []
    for aid in wanted:
        meta = catalog.get(aid, {}).get("meta", {})
        refs.append(AgentRef(
            id=aid,
            label=catalog.get(aid, {}).get("title", aid),
            autonomy=_first(meta.get("Niveau d'autonomie", "")),
            trust=_first(meta.get("Niveau de confiance requis", "")),
            reason=_REASONS.get(aid, "rôle pertinent pour la demande"),
        ))
    return refs


def _first(value: str) -> str:
    value = (value or "").strip()
    return value.split()[0] if value else ""


__all__ = ["select_agents", "SUPERVISOR"]
