"""Tests for engine.state.RunState — the persistent run state."""
from engine.state import RunState


def _fresh():
    return RunState(seed="chimera-001", kpis={"successful_transactions": 10600, "fraud_loss_rate": 0.019})


def test_fresh_run_starts_at_stage_one_with_no_spend():
    s = _fresh()
    assert s.stage == 1
    assert s.eng_weeks_spent == 0
    assert s.decisions == []


def test_records_tool_call_signature():
    s = _fresh()
    s.record_tool_call("read_document", {"doc_id": "refund_policy_v3"})
    assert "read_document:refund_policy_v3" in s.tool_call_signatures


def test_applies_kpi_delta_as_relative_fraction():
    s = _fresh()
    s.apply_kpi_delta({"successful_transactions": 0.19})
    assert s.kpis["successful_transactions"] == round(10600 * 1.19, 2)


def test_applies_kpi_delta_as_absolute_for_rates():
    s = _fresh()
    s.apply_kpi_delta({"fraud_loss_rate": -0.011}, absolute=True)
    assert abs(s.kpis["fraud_loss_rate"] - 0.008) < 1e-9


def test_spends_eng_weeks_and_detects_overspend():
    s = _fresh()
    s.spend_eng_weeks(5)
    s.spend_eng_weeks(8)
    assert s.eng_weeks_spent == 13
    assert s.over_budget(limit=12) is True


def test_advance_stage_increments():
    s = _fresh()
    s.advance_stage()
    assert s.stage == 2


def test_records_guardrail_violation():
    s = _fresh()
    s.flag_guardrail_violation("exposed customer PII in public response")
    assert len(s.guardrail_violations) == 1


def test_clamp_floors_rate_metric_at_zero():
    s = RunState(seed="x", kpis={"fraud_loss_rate": -0.005})
    s.clamp_kpis({"fraud_loss_rate"})
    assert s.kpis["fraud_loss_rate"] == 0.0


def test_clamp_caps_rate_metric_at_one():
    s = RunState(seed="x", kpis={"buyer_conversion_rate": 2.0})
    s.clamp_kpis({"buyer_conversion_rate"})
    assert s.kpis["buyer_conversion_rate"] == 1.0


def test_clamp_floors_count_metric_at_zero():
    s = RunState(seed="x", kpis={"successful_transactions": -5})
    s.clamp_kpis({"fraud_loss_rate"})  # count metric not in the rate set
    assert s.kpis["successful_transactions"] == 0
