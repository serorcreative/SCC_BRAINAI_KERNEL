"""Fixtures des tests du noyau BrainAI.

Le noyau coordonne les composants SCC **réels** (API, Runtime, Control Plane) :
tests d'intégration déterministes. Le répertoire d'exécution est redirigé en tmp.
"""

from __future__ import annotations

import pytest

from scc_brainai.core.config import load_config
from scc_brainai.kernel import BrainAIKernel


@pytest.fixture
def config(tmp_path):
    cfg = load_config()
    cfg.runs_dir = tmp_path / "runs"
    return cfg


@pytest.fixture
def kernel(config):
    return BrainAIKernel(config=config)
