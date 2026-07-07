"""Tests de déterminisme et de la CLI."""

from __future__ import annotations

import json

from scc_brainai.cli import main
from scc_brainai.kernel import BrainAIKernel


def test_default_pipeline_deterministic(config):
    a = BrainAIKernel(config=config).handle("état du système")
    b = BrainAIKernel(config=config).handle("état du système")
    assert json.dumps(a, sort_keys=True, ensure_ascii=False) == \
           json.dumps(b, sort_keys=True, ensure_ascii=False)


def test_deep_pipeline_deterministic(config):
    a = BrainAIKernel(config=config).handle("analyse", options={"deep": True})
    b = BrainAIKernel(config=config).handle("analyse", options={"deep": True})
    assert json.dumps(a, sort_keys=True, ensure_ascii=False) == \
           json.dumps(b, sort_keys=True, ensure_ascii=False)


def test_cli_ask(capsys):
    rc = main(["ask", "état de santé du système"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["ok"] is True
    assert out["intent"] == "inspect"


def test_cli_status(capsys):
    rc = main(["status"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert "deterministic" in out["providers"]["available"]


def test_cli_self_check(capsys):
    rc = main(["self-check"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["ok"] is True


def test_cli_intent(capsys):
    rc = main(["intent", "montre le graphe"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["intent"] == "graph"


def test_cli_providers(capsys):
    rc = main(["providers"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert set(out["external_slots"]) == {"claude", "chatgpt", "gemini"}
