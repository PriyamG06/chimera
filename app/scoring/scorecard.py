"""Scorecard — assembles the 100-point Chimera result (Gate 2: B).

Deterministic half (52) + judge panel half (48) + hard-penalty overrides, clamped to
0..100. Carries the per-dimension breakdown, the deterministic-vs-judge comparison (the
headline chart), and the judge's shadow scores for cross-validation.
"""
from __future__ import annotations
from scoring import deterministic as D
from scoring import judge as J


def build_judge_payload(state, scenario) -> dict:
    """A compact, information-dense summary of the run for the judge — the deliverables,
    the actions taken, and the outcome — instead of a truncated raw transcript prefix.
    """
    deliverables = [{"stage": d["stage"], "kind": d["kind"], "content": d.get("content")}
                    for d in state.decisions if str(d.get("kind", "")).startswith("submit")]
    actions = [{"stage": d["stage"], "kind": d["kind"], "detail": d.get("detail")}
               for d in state.decisions if not str(d.get("kind", "")).startswith("submit")]
    return {
        "deliverables": deliverables,
        "actions": actions,
        "fired_consequences": list(state.fired_rules),
        "eng_weeks_spent": state.eng_weeks_spent,
        "guardrail_violations": list(state.guardrail_violations),
        "final_kpis": dict(state.kpis),
    }


def score_deterministic(state, scenario) -> dict:
    """The objective half + penalties. No LLM, so this never fails on budget/network."""
    deterministic = {
        "investigation": D.score_investigation(state, scenario),
        "execution": D.score_execution(state, scenario),
        "outcomes": D.score_outcomes(state, scenario),
        "safety": D.score_safety(state),
    }
    det_total = round(sum(deterministic.values()), 2)
    return {
        "seed": state.seed,
        "deterministic": {**deterministic, "subtotal": det_total},
        "penalties": D.hard_penalties(state, scenario),
    }


def score_run(state, scenario, transcript=None, judge_fn=None) -> dict:
    payload = build_judge_payload(state, scenario)
    base = score_deterministic(state, scenario)
    det_total = base["deterministic"]["subtotal"]
    penalties = base["penalties"]

    judge = J.score_judge(payload, judge_fn=judge_fn)
    judge_total = judge["total"]

    total = round(min(100.0, max(0.0, det_total + judge_total + penalties)), 2)
    return {
        **base,
        "judge": judge,
        "shadow": J.shadow_scores(payload, judge_fn=judge_fn),
        "total": total,
        "comparison": {"deterministic_total": det_total, "judge_total": judge_total},
    }
