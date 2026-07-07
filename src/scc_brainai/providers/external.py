"""Adaptateurs d'IA externes — emplacements d'extension (non branchés en V1).

Ces classes matérialisent la **place** de Claude, ChatGPT, Gemini, etc., dans
l'architecture. Elles ne réalisent **aucun appel réseau** (contrainte du chantier)
et se déclarent **indisponibles** tant qu'un transport n'est pas fourni. Le noyau
les ignore alors et retombe sur la cognition déterministe.

Brancher une IA (plus tard, sous ADR) = fournir un ``client`` à l'un de ces
adaptateurs (ou une nouvelle sous-classe) ; l'architecture du Kernel ne change pas.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from scc_brainai.providers.base import BaseProvider


class ExternalProvider(BaseProvider):
    """Base des IA externes : indisponible sans ``client`` injecté (aucun réseau ici)."""

    name = "external"

    def __init__(self, client: Optional[Any] = None):
        # ``client`` = futur transport (SDK/HTTP), injecté hors de ce socle.
        self._client = client

    def available(self) -> bool:
        # Aucun client => indisponible. Aucun appel réseau n'est tenté.
        return self._client is not None

    def assist_plan(self, intent: str, query: str, context: Dict[str, Any]) -> Optional[List[str]]:
        if not self.available():
            return None
        # Point d'extension : déléguer au client. Non implémenté en V1 (pas de réseau).
        raise NotImplementedError(
            f"Fournisseur '{self.name}' : transport non implémenté dans le socle (aucun réseau)."
        )

    def assist_synthesis(self, query: str, contributions: List[Dict[str, Any]],
                         context: Dict[str, Any]) -> Optional[str]:
        if not self.available():
            return None
        raise NotImplementedError(
            f"Fournisseur '{self.name}' : transport non implémenté dans le socle (aucun réseau)."
        )


class ClaudeProvider(ExternalProvider):
    name = "claude"


class ChatGPTProvider(ExternalProvider):
    name = "chatgpt"


class GeminiProvider(ExternalProvider):
    name = "gemini"


#: IA externes connues, prêtes à être branchées (toutes indisponibles par défaut).
KNOWN_EXTERNAL = {
    "claude": ClaudeProvider,
    "chatgpt": ChatGPTProvider,
    "gemini": GeminiProvider,
}


__all__ = ["ExternalProvider", "ClaudeProvider", "ChatGPTProvider", "GeminiProvider", "KNOWN_EXTERNAL"]
