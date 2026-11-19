"""Tests for scoring.judge — the 3-model panel judge (Gate 2)."""
import statistics
import pytest
from scoring import judge as J


def const_judge(score):
    def fn(model_id, dimension, variant, payload):
        return {"score": score, "rationale": f"{model_id}/{dimension}/v{variant}"}
    return fn


def test_dimension_scales_median_to_points():
    # every judge, every pass returns 2/3 -> 2/3 of the dimension's points
    out = J.score_dimension("root_cause", 15, J.JUDGE_PANEL, const_judge(2), payload={})
    assert out["points"] == pytest.approx(15 * 2 / 3, abs=0.01)


def test_dimension_reports_inter_judge_spread_when_panel_disagrees():
    def disagree(model_id, dimension, variant, payload):
        score = {"claude-opus-4-8": 3, "gpt-6.1-sol": 1, "gemini-3.8-flash": 0}[model_id]
        return {"score": score, "rationale": ""}
    out = J.score_dimension("product_judgment", 15, J.JUDGE_PANEL, disagree, payload={})
    assert out["spread"] > 0


def test_dimension_runs_two_passes_per_panel_model():
    seen = []
    def record(model_id, dimension, variant, payload):
        seen.append((model_id, variant)); return {"score": 2, "rationale": ""}
    J.score_dimension("stakeholder", 8, J.JUDGE_PANEL, record, payload={})
    assert len(seen) == len(J.JUDGE_PANEL) * 2
    assert {v for _, v in seen} == {0, 1}


def test_score_judge_covers_all_four_dimensions_and_totals():
    result = J.score_judge({"transcript": []}, judge_fn=const_judge(3))
    assert set(result["dimensions"]) == {"root_cause", "product_judgment", "adaptability", "stakeholder"}
    # all max (3/3) -> full 48 points
    assert result["total"] == pytest.approx(48.0, abs=0.01)


def test_shadow_scores_cover_the_deterministic_dimensions():
    out = J.shadow_scores({"transcript": []}, judge_fn=const_judge(2))
    assert set(out) == {"investigation", "execution", "outcomes", "safety"}


# --- robust parsing of real model replies ---
def test_parse_plain_json():
    assert J._parse_judge('{"score": 2, "rationale": "ok"}')["score"] == 2


def test_parse_json_wrapped_in_markdown_fences():
    assert J._parse_judge('```json\n{"score": 3, "rationale": "great"}\n```')["score"] == 3


def test_parse_json_embedded_in_prose():
    assert J._parse_judge('Here is my rating:\n{"score": 1, "rationale": "weak"}\nThanks.')["score"] == 1


def test_parse_clamps_out_of_range_score():
    assert J._parse_judge('{"score": 7, "rationale": "x"}')["score"] == 3


def test_parse_unparseable_defaults_to_zero():
    assert J._parse_judge("I cannot score this.")["score"] == 0
