"""Tests : classification d'intention et fournisseurs d'intelligence."""

from __future__ import annotations

from scc_brainai.kernel import classify_intent
from scc_brainai.providers.registry import ProviderRegistry


def test_intent_classification():
    assert classify_intent("Quelles doctrines gouvernent ceci ?") == "governance"
    assert classify_intent("état de santé du système") == "inspect"
    assert classify_intent("montre le graphe et ses relations") == "graph"
    assert classify_intent("analyse et raisonne sur l'architecture") == "cognition"
    assert classify_intent("bonjour") == "general"


def test_intent_forced():
    assert classify_intent("bonjour", forced="graph") == "graph"
    assert classify_intent("bonjour", forced="nonsense") == "general"


def test_registry_deterministic_always_available():
    reg = ProviderRegistry()
    assert "deterministic" in reg.available()
    # les IA externes sont enregistrées mais indisponibles (aucun réseau)
    for name in ("claude", "chatgpt", "gemini"):
        assert name in reg.names()
        assert name not in reg.available()


def test_registry_fallback_to_deterministic():
    reg = ProviderRegistry()
    # même en demandant une IA externe, on retombe sur le déterministe
    chosen = reg.select(["claude", "chatgpt", "gemini"])
    assert chosen.name == "deterministic"


def test_registry_select_respects_order_when_available():
    reg = ProviderRegistry()
    chosen = reg.select(["deterministic"])
    assert chosen.name == "deterministic"
