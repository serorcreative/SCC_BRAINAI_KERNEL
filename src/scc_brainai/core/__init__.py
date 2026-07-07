"""Noyau du kernel BrainAI : configuration, erreurs, modèle."""

from __future__ import annotations

from scc_brainai.core.config import BrainAIConfig, load_config
from scc_brainai.core.errors import (
    BrainAIError,
    ConfigError,
    PlanningError,
    ProviderUnavailable,
    SourceUnavailable,
)
from scc_brainai.core.model import (
    AgentRef,
    Contribution,
    Intent,
    Plan,
    PlanStep,
    Request,
)

__all__ = [
    "BrainAIConfig",
    "load_config",
    "BrainAIError",
    "ConfigError",
    "SourceUnavailable",
    "ProviderUnavailable",
    "PlanningError",
    "Intent",
    "Request",
    "AgentRef",
    "PlanStep",
    "Plan",
    "Contribution",
]
