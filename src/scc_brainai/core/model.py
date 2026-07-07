"""Modèle du noyau BrainAI : demande, contexte, plan, contributions, réponse.

Structures pures, sérialisables, déterministes. Le vocabulaire (Intent, Agent,
Plan, Contribution) s'aligne sur le méta-modèle SCC (un Agent est un rôle ; un
Workflow est un plan ; BrainAI *incarne* et *orchestre* des Agents).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Intent(str, Enum):
    """Intention déterministe déduite de la demande."""

    COGNITION = "cognition"        # comprendre / raisonner / analyser (chaîne des moteurs)
    GOVERNANCE = "governance"      # doctrines / ADR / règles
    GRAPH = "graph"                # explorer la structure de SCC
    INSPECT = "inspect"            # état / santé / supervision
    GENERAL = "general"            # demande transverse


@dataclass
class Request:
    """Demande utilisateur adressée à BrainAI."""

    query: str
    actor: str = "brainai"
    autonomy: str = "A3"
    intent: Optional[str] = None            # forçage éventuel de l'intention
    options: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"query": self.query, "actor": self.actor, "autonomy": self.autonomy,
                "intent": self.intent, "options": dict(self.options)}


@dataclass
class AgentRef:
    """Rôle d'agent sélectionné pour la demande."""

    id: str
    label: str = ""
    autonomy: str = ""
    trust: str = ""
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "label": self.label, "autonomy": self.autonomy,
                "trust": self.trust, "reason": self.reason}


@dataclass
class PlanStep:
    """Étape du plan d'exécution, confiée à un agent."""

    id: str
    agent: str
    action: str
    description: str
    doctrines: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "agent": self.agent, "action": self.action,
                "description": self.description, "doctrines": list(self.doctrines)}


@dataclass
class Plan:
    """Plan d'exécution construit par le noyau."""

    intent: str
    rationale: str
    steps: List[PlanStep] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"intent": self.intent, "rationale": self.rationale,
                "steps": [s.to_dict() for s in self.steps]}


@dataclass
class Contribution:
    """Résultat de l'exécution d'une étape par un agent."""

    step_id: str
    agent: str
    action: str
    status: str
    findings: Dict[str, Any] = field(default_factory=dict)
    provider: str = "deterministic"

    def to_dict(self) -> Dict[str, Any]:
        return {"step_id": self.step_id, "agent": self.agent, "action": self.action,
                "status": self.status, "provider": self.provider, "findings": self.findings}


__all__ = ["Intent", "Request", "AgentRef", "PlanStep", "Plan", "Contribution"]
