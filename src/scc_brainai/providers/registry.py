"""Registre des fournisseurs d'intelligence — sélection avec repli déterministe.

Plusieurs IA peuvent être enregistrées (Claude, ChatGPT, Gemini…) sans modifier
le noyau. La sélection suit un ordre de préférence et **retombe toujours** sur le
fournisseur déterministe : BrainAI ne dépend d'aucune IA externe.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from scc_brainai.providers.base import BaseProvider
from scc_brainai.providers.deterministic import DeterministicProvider
from scc_brainai.providers.external import KNOWN_EXTERNAL


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: Dict[str, BaseProvider] = {}
        # Toujours présent : la cognition déterministe (repli garanti).
        self.register(DeterministicProvider())
        # Emplacements d'IA externes connues (indisponibles tant que non configurées).
        for name, cls in KNOWN_EXTERNAL.items():
            self.register(cls())

    def register(self, provider: BaseProvider) -> BaseProvider:
        self._providers[provider.name] = provider
        return provider

    def get(self, name: str) -> Optional[BaseProvider]:
        return self._providers.get(name)

    def names(self) -> List[str]:
        return sorted(self._providers)

    def available(self) -> List[str]:
        return sorted(n for n, p in self._providers.items() if p.available())

    def select(self, order: Optional[List[str]] = None) -> BaseProvider:
        """Retourne le premier fournisseur *disponible* selon l'ordre de préférence,
        avec repli garanti sur le fournisseur déterministe."""
        for name in (order or []):
            p = self._providers.get(name)
            if p is not None and p.available():
                return p
        # repli garanti
        return self._providers["deterministic"]

    def to_dict(self) -> Dict[str, object]:
        return {
            "registered": self.names(),
            "available": self.available(),
            "external_slots": sorted(KNOWN_EXTERNAL),
        }


__all__ = ["ProviderRegistry"]
