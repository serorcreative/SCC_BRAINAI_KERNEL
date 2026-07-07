"""Fournisseurs d'intelligence : déterministe (défaut) + emplacements IA externes."""

from __future__ import annotations

from scc_brainai.providers.base import BaseProvider, IntelligenceProvider
from scc_brainai.providers.deterministic import DeterministicProvider
from scc_brainai.providers.external import (
    ChatGPTProvider,
    ClaudeProvider,
    ExternalProvider,
    GeminiProvider,
)
from scc_brainai.providers.registry import ProviderRegistry

__all__ = [
    "IntelligenceProvider",
    "BaseProvider",
    "DeterministicProvider",
    "ExternalProvider",
    "ClaudeProvider",
    "ChatGPTProvider",
    "GeminiProvider",
    "ProviderRegistry",
]
