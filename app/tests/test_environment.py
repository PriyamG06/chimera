"""Tests for engine.environment.Environment — tool dispatch + consequence tree."""
from pathlib import Path
import pytest
from engine.scenario import Scenario
from engine.environment import Environment

SCENARIO_DIR = Path(__file__).resolve().parents[1] / "scenario"


@pytest.fixture
def env():
    return Environment(Scenario(SCENARIO_DIR))


# --- baseline ---
def test_initial_kpis_seeded_from_mission_baseline(env):
    assert env.state.kpis["successful_transactions"] == 10600
    assert env.state.kpis["fraud_loss_rate"] == 0.019


# --- tool dispatch ---
def test_call_tool_records_signature(env):
    env.call_tool("read_document", {"doc_id": "refund_policy_v3"})
    assert "read_document:refund_policy_v3" in env.state.tool_call_signatures


def test_query_sql_returns_rows(env):
    out = env.call_tool("query_sql", {"query": "SELECT COUNT(*) AS n FROM events"})
    assert out["rows"][0]["n"] == 55737


def test_query_sql_blocks_writes(env):
    out = env.call_tool("query_sql", {"query": "DELETE FROM events"})
    assert out["error"]
    assert env.call_tool("query_sql", {"query": "SELECT COUNT(*) AS n FROM events"})["rows"][0]["n"] == 55737


def test_message_stakeholder_matches_topic(env):
    out = env.call_tool("message_stakeholder", {"persona_id": "head_risk", "message": "what is happening with fraud?"})
    assert "refund" in out["reply"].lower()


def test_message_stakeholder_falls_back_to_default(env):
    out = env.call_tool("message_stakeholder", {"persona_id": "ceo", "message": "zxcv nonsense"})
    assert out["reply"]  # returns the persona default, never empty


# --- consequence tree ---
def test_correct_refund_fix_lowers_fraud_and_costs_one_week(env):
    out = env.call_tool("adjust_agent_policy", {"agent_id": "support", "policy": {"auto_refund_ceiling": 50}})
    assert "fix_refund_agent_correct" in out["fired_rules"]
    assert abs(env.state.kpis["fraud_loss_rate"] - 0.008) < 1e-9
    assert env.state.eng_weeks_spent == 1


def test_fired_rules_are_recorded_on_state(env):
    env.call_tool("adjust_agent_policy", {"agent_id": "support", "policy": {"auto_refund_ceiling": 50}})
    assert "fix_refund_agent_correct" in env.state.fired_rules


def test_loosening_refunds_unlocks_crisis_incident(env):
    out = env.call_tool("adjust_agent_policy", {"agent_id": "support", "policy": {"auto_refund_ceiling": 250}})
    assert "expand_auto_refund_wrong" in out["fired_rules"]
    assert any(i == "false_refund_blowup" for i, _ in env.state.incidents_queued)


def test_refund_ceiling_200_fires_neither_rule(env):
    out = env.call_tool("adjust_agent_policy", {"agent_id": "support", "policy": {"auto_refund_ceiling": 200}})
    assert "fix_refund_agent_correct" not in out["fired_rules"]
    assert "expand_auto_refund_wrong" not in out["fired_rules"]


def test_informed_recommendation_fix_is_the_big_lever(env):
    env.call_tool("read_document", {"doc_id": "rn_2026_10"})
    out = env.call_tool("launch_experiment", {"spec": {"name": "new_creator_discovery_boost"}})
    assert "fix_recommendation_controlled" in out["fired_rules"]
    assert env.state.kpis["successful_transactions"] == round(10600 * 1.19, 2)


def test_naive_recommendation_fix_backfires(env):
    out = env.call_tool("launch_experiment", {"spec": {"name": "new_creator_discovery_boost"}})
    assert "boost_new_creators_naive" in out["fired_rules"]
    assert "fix_recommendation_controlled" not in out["fired_rules"]
    assert any(i == "low_quality_surfacing" for i, _ in env.state.incidents_queued)


def test_creator_incentive_flood_queues_flood_incident(env):
    env.call_tool("set_feature_flag", {"flag": "creator_incentive_bonus", "value": True})
    assert any(i == "low_quality_flood" for i, _ in env.state.incidents_queued)


def test_mobile_checkout_rollback_fixes_conversion(env):
    out = env.call_tool("rollback", {"change_id": "RN-2026-09"})
    assert "fix_mobile_checkout_rollback" in out["fired_rules"]
    assert env.state.kpis["successful_transactions"] == round(10600 * 1.07, 2)


def test_platform_rewrite_distractor_burns_whole_budget(env):
    env.call_tool("launch_experiment", {"spec": {"name": "architecture_rewrite"}})
    assert env.state.eng_weeks_spent == 12


# --- tool schemas for the runner ---
def test_exposes_openai_tool_schemas(env):
    names = {t["function"]["name"] for t in env.tool_schemas()}
    assert {"query_sql", "read_document", "message_stakeholder", "adjust_agent_policy",
            "launch_experiment", "rollback", "submit_diagnosis"} <= names


# --- intent-based matching: real models use their own vocabulary, not our identifiers.
# These reproduce the exact args claude-haiku-4-5 emitted in the first full run.
def test_refund_fix_fires_despite_different_field_name(env):
    out = env.call_tool("adjust_agent_policy",
                        {"agent_id": "support",
                         "policy": {"auto_refund_ceiling_usd": 50, "manual_review_threshold_usd": 50}})
    assert "fix_refund_agent_correct" in out["fired_rules"]


def test_mobile_checkout_fix_fires_on_descriptive_flag_name(env):
    out = env.call_tool("set_feature_flag", {"flag": "mobile_wallet_validation_fix_enabled", "value": True})
    assert "fix_mobile_checkout_flag" in out["fired_rules"]


def test_recommendation_fix_fires_on_descriptive_spec(env):
    env.call_tool("read_document", {"doc_id": "rn_2026_10"})
    out = env.call_tool("launch_experiment", {"spec": {
        "hypothesis": "Rebalancing recommendations to give new and long-tail creators discovery "
                      "will lift transactions",
        "control": {"description": "Current recommendation model RN-2026-10, engagement-optimized"},
        "treatment": {"description": "Boost new-creator visibility in discovery"}}})
    assert "fix_recommendation_controlled" in out["fired_rules"]


def test_incentive_with_quality_gate_does_not_trigger_flood(env):
    # the model paired the incentive with a quality gate — the smart move should NOT be punished
    env.call_tool("set_feature_flag", {"flag": "creator_quality_gate_enabled", "value": True})
    env.call_tool("set_feature_flag", {"flag": "creator_incentive_bonus_enabled", "value": True})
    assert not any(i == "low_quality_flood" for i, _ in env.state.incidents_queued)


def test_incentive_without_quality_gate_still_triggers_flood(env):
    env.call_tool("set_feature_flag", {"flag": "creator_incentive_bonus_enabled", "value": True})
    assert any(i == "low_quality_flood" for i, _ in env.state.incidents_queued)


# --- fire-once-per-problem-group: repeating a fix must not stack its effect ---
def test_same_fix_fires_only_once(env):
    env.call_tool("adjust_agent_policy", {"agent_id": "support", "policy": {"auto_refund_ceiling": 50}})
    env.call_tool("adjust_agent_policy", {"agent_id": "support", "policy": {"auto_refund_ceiling": 50}})
    assert abs(env.state.kpis["fraud_loss_rate"] - 0.008) < 1e-9  # delta applied once, not twice


def test_two_tools_fixing_same_problem_count_once(env):
    env.call_tool("set_feature_flag", {"flag": "mobile_wallet_fix", "value": True})
    env.call_tool("rollback", {"change_id": "RN-2026-09"})
    assert env.state.kpis["successful_transactions"] == round(10600 * 1.07, 2)


def test_baseline_seeds_agent_task_completion(env):
    assert env.state.kpis["ai_agent_task_completion"] == 0.78


def test_fraud_cannot_go_negative_via_clamp(env):
    # two different refund-area rules can't both fire (group dedupe), and clamp floors at 0 regardless
    env.call_tool("adjust_agent_policy", {"agent_id": "support", "policy": {"auto_refund_ceiling": 50}})
    assert env.state.kpis["fraud_loss_rate"] >= 0
