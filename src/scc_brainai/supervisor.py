"""KernelSupervisor — BrainAI *incarne* le superviseur du Runtime.

Le Runtime (07) expose ``SupervisorPort`` (``on_plan`` / ``on_review`` /
``on_decision``) comme point de branchement officiel de BrainAI. Ce superviseur
l'implémente : BrainAI supervise l'exécution **sans jamais court-circuiter la
gouvernance** (règle dure T3, vetos) — il *conseille et observe*, il ne *décide pas*.

Conforme au méta-modèle : « BrainAI *incarne* l'Agent Superviseur (SCC-AGENT-0020) ».
Consultatif et déterministe ; peut solliciter un fournisseur d'intelligence sans
jamais en dépendre.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class KernelSupervisor:
    """Superviseur BrainAI branché sur le Runtime (duck-typé sur ``SupervisorPort``)."""

    name = "brainai"

    def __init__(self, provider=None):
        self._provider = provider
        self.plans: List[str] = []
        self.reviews: List[str] = []
        self.decisions: List[str] = []

    def on_plan(self, job, context) -> Optional[Dict[str, Any]]:
        self.plans.append(getattr(job, "id", ""))
        return {"planned_by": self.name, "kind": getattr(job, "kind", "")}

    def on_review(self, job, result, context) -> Optional[Dict[str, Any]]:
        self.reviews.append(getattr(job, "id", ""))
        return {"reviewed_by": self.name}

    def on_decision(self, job, decision, context) -> Optional[str]:
        # Avis consultatif uniquement : la gouvernance reste souveraine.
        self.decisions.append(getattr(job, "id", ""))
        return None

    def summary(self) -> Dict[str, Any]:
        return {"name": self.name, "plans": len(self.plans),
                "reviews": len(self.reviews), "decisions": len(self.decisions)}


__all__ = ["KernelSupervisor"]
