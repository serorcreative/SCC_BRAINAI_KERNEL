"""SCC BrainAI Kernel — noyau officiel, chef d'orchestre cognitif de SCC.

BrainAI **coordonne** les composants de Seror Créative Core (API, Runtime, Control
Plane, graphe, doctrines, ADR) sans en remplacer ni modifier aucun. Il reçoit une
demande, construit un contexte, planifie, sélectionne et orchestre des Agents sous
gouvernance, consolide et répond — **de façon déterministe**.

Les IA externes (Claude, ChatGPT, Gemini…) sont des **capacités optionnelles**
branchables via :class:`~scc_brainai.providers.registry.ProviderRegistry` ; le
noyau fonctionne pleinement **sans aucune IA** (cognition déterministe par défaut).

Principes : aucun composant modifié (interfaces publiques seules) ; aucun LLM
obligatoire ; aucun réseau ; stdlib pur ; déterminisme complet.
"""

from __future__ import annotations

__version__ = "1.0.0"

from scc_brainai.core.config import BrainAIConfig, load_config
from scc_brainai.core.model import Request
from scc_brainai.kernel import BrainAIKernel, classify_intent
from scc_brainai.providers.registry import ProviderRegistry

__all__ = [
    "__version__",
    "BrainAIKernel",
    "classify_intent",
    "BrainAIConfig",
    "load_config",
    "Request",
    "ProviderRegistry",
]
