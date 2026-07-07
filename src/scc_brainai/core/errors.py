"""Hiérarchie d'exceptions du noyau BrainAI."""

from __future__ import annotations


class BrainAIError(Exception):
    """Erreur de base du noyau BrainAI."""


class ConfigError(BrainAIError):
    """Configuration absente, illisible ou invalide."""


class SourceUnavailable(BrainAIError):
    """Une source SCC (API, Runtime, Control Plane) est introuvable/importable."""


class ProviderUnavailable(BrainAIError):
    """Un fournisseur d'intelligence (IA externe) n'est pas disponible/configuré."""


class PlanningError(BrainAIError):
    """Impossible de construire un plan d'exécution pour la demande."""


__all__ = [
    "BrainAIError",
    "ConfigError",
    "SourceUnavailable",
    "ProviderUnavailable",
    "PlanningError",
]
