"""RunState — the persistent state of one model's run through the gauntlet.

Decisions, KPI changes, spend, and tool calls all accumulate here across the six
stages. This is what makes the benchmark stateful: a Stage-3 action is recorded and
can drive a Stage-5 consequence.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class RunState:
    seed: str
    kpis: dict
    stage: int = 1
    current_day: int = 0
    eng_weeks_spent: float = 0.0
    decisions: list = field(default_factory=list)
    flags_set: dict = field(default_factory=dict)
    incidents_fired: list = field(default_factory=list)
    incidents_queued: list = field(default_factory=list)   # (incident_id, reveal_day)
    guardrail_violations: list = field(default_factory=list)
    claimed_actions: list = field(default_factory=list)
    tool_call_signatures: list = field(default_factory=list)
    query_log: list = field(default_factory=list)
    fired_rules: list = field(default_factory=list)
    fired_groups: list = field(default_factory=list)

    def record_tool_call(self, name: str, args: dict) -> None:
        key = args.get("doc_id") or args.get("agent_id") or args.get("persona_id") \
            or args.get("flag") or args.get("change_id") or args.get("topic") or ""
        self.tool_call_signatures.append(f"{name}:{key}" if key else name)

    def apply_kpi_delta(self, delta: dict, absolute: bool = False) -> None:
        for metric, change in delta.items():
            current = self.kpis.get(metric, 0)
            if absolute:
                self.kpis[metric] = round(current + change, 9)
            else:
                self.kpis[metric] = round(current * (1 + change), 2)

    def spend_eng_weeks(self, weeks: float) -> None:
        self.eng_weeks_spent += weeks

    def over_budget(self, limit: float = 12) -> bool:
        return self.eng_weeks_spent > limit

    def advance_stage(self) -> None:
        self.stage += 1

    def flag_guardrail_violation(self, description: str) -> None:
        self.guardrail_violations.append(description)

    def clamp_kpis(self, rate_metrics) -> None:
        """Keep metrics physical: rates in [0,1], counts >= 0."""
        for metric, value in self.kpis.items():
            if metric in rate_metrics:
                self.kpis[metric] = round(min(1.0, max(0.0, value)), 9)
            else:
                self.kpis[metric] = max(0, value)
