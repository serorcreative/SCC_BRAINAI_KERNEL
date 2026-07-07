"""Contrat des fournisseurs d'intelligence — le point d'extension multi-IA.

BrainAI **fonctionne sans aucune IA externe** : sa cognition par défaut est
déterministe (règles). Une IA (Claude, ChatGPT, Gemini, …) est une **capacité
optionnelle** qui *augmente* le noyau sans jamais en être un prérequis.

Le contrat est volontairement minimal et *augmentatif* : un fournisseur ne décide
rien, il **enrichit** (indices de plan, prose de synthèse). Le noyau reste maître
de la planification, de la sélection d'agents et de l'orchestration.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class IntelligenceProvider(Protocol):
    """Fournisseur d'intelligence branchable (déterministe ou IA externe future)."""

    name: str

    def available(self) -> bool:
        """Vrai si le fournisseur peut être sollicité (configuré, joignable)."""

    def assist_plan(self, intent: str, query: str, context: Dict[str, Any]) -> Optional[List[str]]:
        """Indices consultatifs pour affiner le plan (ou None)."""

    def assist_synthesis(self, query: str, contributions: List[Dict[str, Any]],
                         context: Dict[str, Any]) -> Optional[str]:
        """Synthèse en langage naturel (ou None si non disponible)."""


class BaseProvider:
    """Base commune : indisponible par défaut, hooks inertes."""

    name = "base"

    def available(self) -> bool:
        return False

    def assist_plan(self, intent: str, query: str, context: Dict[str, Any]) -> Optional[List[str]]:
        return None

    def assist_synthesis(self, query: str, contributions: List[Dict[str, Any]],
                         context: Dict[str, Any]) -> Optional[str]:
        return None


__all__ = ["IntelligenceProvider", "BaseProvider"]
