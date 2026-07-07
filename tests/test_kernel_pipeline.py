"""Tests du pipeline complet du noyau (demande → réponse structurée)."""

from __future__ import annotations


def test_self_check(kernel):
    sc = kernel.self_check()
    assert sc["ok"] is True
    labels = {c["label"] for c in sc["checks"]}
    assert {"api_source", "runtime_source", "control_plane_source",
            "works_without_external_ai", "no_llm_no_network"} <= labels


def test_status_sources_and_providers(kernel):
    st = kernel.status()
    assert st["sources"]["api"] is True
    assert st["sources"]["runtime"] is True
    assert st["sources"]["control_plane"] is True
    assert "deterministic" in st["providers"]["available"]


def test_handle_response_shape(kernel):
    r = kernel.handle("état de santé du système")
    for key in ("ok", "intent", "context", "agents", "plan", "governance",
                "runtime", "supervisor", "contributions", "synthesis", "provider"):
        assert key in r, f"clé manquante : {key}"
    assert r["ok"] is True
    assert r["provider"]["selected"] == "deterministic"


def test_governance_intent_consults_doctrines(kernel):
    r = kernel.handle("Quelles doctrines et ADR gouvernent la gouvernance ?")
    assert r["intent"] == "governance"
    assert r["governance"]["count_doctrines"] > 0
    # au moins un agent de gouvernance sélectionné
    assert any(a["id"] == "SCC-AGENT-0002" for a in r["agents"])


def test_cognition_selects_engine_agents(kernel):
    r = kernel.handle("analyse l'architecture de raisonnement")
    assert r["intent"] == "cognition"
    ids = {a["id"] for a in r["agents"]}
    assert {"SCC-AGENT-0006", "SCC-AGENT-0010"} <= ids  # ingestion..raisonnement


def test_supervisor_always_incarnated(kernel):
    r = kernel.handle("bonjour")
    assert any(a["id"] == "SCC-AGENT-0020" for a in r["agents"])
    assert r["supervisor"]["name"] == "brainai"
    assert r["supervisor"]["plans"] >= 1


def test_runtime_job_governed(kernel):
    r = kernel.handle("état du système")
    assert r["runtime"]["status"] == "succeeded"
    assert r["runtime"]["kind"] == "echo"


def test_deep_cognition_runs_brain_pass(kernel):
    r = kernel.handle("analyse architecture", options={"deep": True})
    assert r["runtime"]["kind"] == "brain_pass"
    assert r["runtime"]["status"] == "succeeded"
    know = next(c for c in r["contributions"] if c["agent"] == "SCC-AGENT-0009")
    assert "knowledge" in know["findings"].get("stage_summary", {})


def test_works_without_any_external_ai(kernel):
    # aucune IA externe disponible -> le noyau répond quand même
    r = kernel.handle("explique l'architecture")
    assert r["ok"] is True
    assert r["provider"]["selected"] == "deterministic"
    assert r["synthesis"]
