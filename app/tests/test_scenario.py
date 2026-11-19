"""Tests for engine.scenario.Scenario — loads the authored world."""
from pathlib import Path
import pytest
from engine.scenario import Scenario

SCENARIO_DIR = Path(__file__).resolve().parents[1] / "scenario"


@pytest.fixture
def scenario():
    return Scenario(SCENARIO_DIR)


def test_loads_starting_kpis(scenario):
    assert scenario.starting_kpis()["successful_transactions"] == 31800


def test_exposes_mission_target_and_guardrails(scenario):
    m = scenario.mission()
    assert m["target_transactions_monthly"] == 13250
    assert m["guardrails"]["fraud_loss_rate"]["ceiling"] == 0.025


def test_lists_documents_from_manifest(scenario):
    ids = {d["id"] for d in scenario.list_documents()}
    assert {"refund_policy_v3", "refund_reversal", "rn_2026_10"} <= ids


def test_reads_document_body(scenario):
    body = scenario.read_document("refund_reversal")
    assert "$50" in body


def test_unknown_document_raises(scenario):
    with pytest.raises(KeyError):
        scenario.read_document("does_not_exist")


def test_loads_consequence_rules(scenario):
    ids = {r["id"] for r in scenario.consequence_rules()}
    assert "fix_refund_agent_correct" in ids


def test_loads_incidents_including_unlocked_crisis(scenario):
    inc = scenario.incidents()
    assert "false_refund_blowup" in inc
    assert inc["false_refund_blowup"]["unlocked_by"] == "expand_auto_refund_wrong"


def test_loads_stakeholders(scenario):
    s = scenario.stakeholders()
    assert "ceo" in s and "head_risk" in s
    assert s["head_risk"]["responses"]["fraud"]


def test_gm_truth_is_loaded_but_separate(scenario):
    # gm_truth must be accessible to scoring but never bundled into agent-facing data
    assert "rc1_rogue_refund_agent" == scenario.gm_truth()["root_cause_1"]["id"]
