"""Fournisseur d'intelligence **déterministe** — la cognition par défaut de BrainAI.

Aucun LLM, aucun réseau : la « pensée » du noyau est ici une composition de règles
pures et lisibles. C'est ce fournisseur qui garantit que BrainAI **fonctionne
toujours**, même sans aucune IA externe.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from scc_brainai.providers.base import BaseProvider

_INTENT_HINTS = {
    "cognition": [
        "Exécuter la chaîne cognitive (ingestion → raisonnement) sous gouvernance.",
        "Citer les connaissances ancrées produites par le raisonnement.",
    ],
    "governance": [
        "Consulter les doctrines gouvernant les agents concernés.",
        "Référencer les ADR pertinents (décisions figées).",
    ],
    "graph": [
        "Explorer les nœuds et relations pertinents du graphe SCC.",
        "Suivre les relations du méta-modèle (uses, governs, produces…).",
    ],
    "inspect": [
        "Interroger le Control Plane pour la santé consolidée.",
        "Relever les alertes et l'état de préparation.",
    ],
    "general": [
        "Croiser structure (graphe), gouvernance (doctrines/ADR) et santé (Control Plane).",
    ],
}


class DeterministicProvider(BaseProvider):
    """Cognition par règles — toujours disponible, entièrement déterministe."""

    name = "deterministic"

    def available(self) -> bool:
        return True

    def assist_plan(self, intent: str, query: str, context: Dict[str, Any]) -> Optional[List[str]]:
        return list(_INTENT_HINTS.get(intent, _INTENT_HINTS["general"]))

    def assist_synthesis(self, query: str, contributions: List[Dict[str, Any]],
                         context: Dict[str, Any]) -> Optional[str]:
        # Synthèse structurée déterministe : agrège les constats des agents.
        lines: List[str] = []
        health = context.get("health", {}).get("overall", "unknown")
        readiness = context.get("readiness", {}).get("verdict", "unknown")
        lines.append(f"Demande : « {query.strip()} ».")
        lines.append(f"État du système : santé « {health} », préparation « {readiness} ».")
        ok = sum(1 for c in contributions if c.get("status") == "ok")
        lines.append(f"{ok}/{len(contributions)} contribution(s) d'agent aboutie(s).")
        for c in contributions:
            summary = _summarize(c)
            if summary:
                lines.append(f"- [{c['agent']}] {summary}")
        lines.append("Réponse produite sans IA externe (cognition déterministe de BrainAI).")
        return "\n".join(lines)


def _summarize(contribution: Dict[str, Any]) -> str:
    f = contribution.get("findings", {})
    action = contribution.get("action", "")
    if "stage_summary" in f:
        stages = ", ".join(sorted(f["stage_summary"].keys()))
        return f"passe cognitive : étapes {stages}."
    if "doctrines" in f:
        return f"{len(f['doctrines'])} doctrine(s) pertinente(s) ; {len(f.get('adrs', []))} ADR."
    if "graph" in f:
        g = f["graph"]
        return f"graphe : {g.get('nodes')} nœuds, {g.get('edges')} relations."
    if "health" in f:
        return f"santé consolidée : {f['health']}."
    if "echo" in f:
        return "job Runtime de diagnostic exécuté (gouverné)."
    return action


__all__ = ["DeterministicProvider"]
