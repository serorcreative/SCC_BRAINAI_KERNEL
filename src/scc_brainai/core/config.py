"""Configuration du noyau BrainAI (JSON, sans dépendance).

BrainAI est le **chef d'orchestre cognitif** : il coordonne les composants SCC déjà
construits via leurs interfaces publiques (API `08`, Runtime `07`, Control Plane
`09`). Il ne possède ni ne modifie aucun d'eux.

Déterminisme : ``as_of`` fige l'horodatage de toute exécution.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from scc_brainai.core.errors import ConfigError

BRAINAI_ROOT = Path(__file__).resolve().parents[3]        # .../10_BRAINAI
DEFAULT_SCC_ROOT = BRAINAI_ROOT.parent                     # .../01_CCSC
DEFAULT_CONFIG_PATH = BRAINAI_ROOT / "config" / "brainai.json"

DEFAULT_AS_OF = "2026-07-06T00:00:00+00:00"


@dataclass
class BrainAIConfig:
    """Emplacements coordonnés et paramètres déterministes."""

    brainai_root: Path = BRAINAI_ROOT
    scc_root: Path = DEFAULT_SCC_ROOT
    runs_dir: Path = BRAINAI_ROOT / "runs"
    as_of: str = DEFAULT_AS_OF
    default_actor: str = "brainai"
    default_autonomy: str = "A3"
    # Ordre de préférence des fournisseurs d'intelligence (repli déterministe).
    provider_order: List[str] = field(default_factory=lambda: ["deterministic"])
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def api_src(self) -> Path:
        return self.scc_root / "08_API" / "src"

    @property
    def runtime_src(self) -> Path:
        return self.scc_root / "07_RUNTIME" / "src"

    @property
    def control_plane_src(self) -> Path:
        return self.scc_root / "09_CONTROL_PLANE" / "src"

    def ensure_directories(self) -> None:
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "brainai_root": str(self.brainai_root),
            "scc_root": str(self.scc_root),
            "runs_dir": str(self.runs_dir),
            "as_of": self.as_of,
            "default_actor": self.default_actor,
            "default_autonomy": self.default_autonomy,
            "provider_order": list(self.provider_order),
        }


def _resolve(base: Path, value: str) -> Path:
    p = Path(value).expanduser()
    return p if p.is_absolute() else (base / p).resolve()


def load_config(path: Optional[Path] = None) -> BrainAIConfig:
    config = BrainAIConfig()
    target = Path(path) if path else DEFAULT_CONFIG_PATH
    if not target.exists():
        if path is not None:
            raise ConfigError(f"Configuration introuvable : {target}")
        return config
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"Configuration illisible ({target}) : {exc}") from exc

    base = config.brainai_root
    if "scc_root" in raw:
        config.scc_root = _resolve(base, raw["scc_root"])
    paths = raw.get("paths", {})
    if "runs_dir" in paths:
        config.runs_dir = _resolve(base, paths["runs_dir"])
    config.as_of = str(raw.get("as_of", DEFAULT_AS_OF))
    config.default_actor = str(raw.get("default_actor", config.default_actor))
    config.default_autonomy = str(raw.get("default_autonomy", config.default_autonomy))
    config.provider_order = list(raw.get("provider_order", config.provider_order))
    config.extra = dict(raw.get("extra", {}))
    return config


__all__ = ["BRAINAI_ROOT", "DEFAULT_SCC_ROOT", "DEFAULT_AS_OF", "BrainAIConfig", "load_config"]
