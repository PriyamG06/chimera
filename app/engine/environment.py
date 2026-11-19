"""Environment — holds the scenario + run state, dispatches tools, and evaluates the
consequence tree so decisions persist across stages.
"""
from __future__ import annotations
import re
import json
from engine.state import RunState
from engine import tools as T

# Rate/ratio metrics get absolute (percentage-point) deltas; counts get relative fractions.
RATE_METRICS = {"fraud_loss_rate", "creator_30d_retention", "buyer_conversion_rate",
                "avg_creator_quality", "net_margin", "ai_agent_task_completion", "support_csat"}


def _norm(s) -> str:
    """Lowercase and turn _ and - into spaces, so identifiers match natural-language concepts."""
    return re.sub(r"[_\-]+", " ", str(s).lower())


class Environment:
    def __init__(self, scenario):
        self.scenario = scenario
        self.state = RunState(seed=scenario._world["seed"], kpis=self._baseline_kpis())

    def _baseline_kpis(self):
        m = self.scenario.mission()
        g = m["guardrails"]
        hm = self.scenario._world["public_dashboard"]["headline_metrics"]
        return {
            "successful_transactions": m["baseline_transactions_monthly"],
            "fraud_loss_rate": g["fraud_loss_rate"]["current"],
            "creator_30d_retention": g["creator_30d_retention"]["current"],
            "buyer_conversion_rate": hm["buyer_conversion_rate"]["value"],
            "creator_signups": hm["creator_signups"]["value"],
            "gmv_usd": hm["gmv_usd"]["value"],
            "ai_agent_task_completion": hm["ai_agent_task_completion"]["value"],
            "support_csat": hm["support_csat"]["value"],
            "avg_creator_quality": 0.80,   # synthetic index; only the incentive-flood moves it
            "net_margin": 0.30,            # synthetic index; only the take-rate distractor moves it
        }

    # --- dispatch ---
    def call_tool(self, name: str, args: dict) -> dict:
        if name not in T.TOOLS:
            return {"error": f"unknown tool: {name}"}
        self.state.record_tool_call(name, args)
        result = T.TOOLS[name](self, args)
        fired = self._apply_consequences(name, args)
        if fired:
            result = {**result, "fired_rules": fired}
        else:
            result.setdefault("fired_rules", [])
        return result

    def tool_schemas(self):
        return T.TOOL_SCHEMAS

    # --- consequence tree ---
    def _apply_consequences(self, name, args):
        fired = []
        for rule in self.scenario.consequence_rules():
            group = rule.get("group")
            if group and group in self.state.fired_groups:
                continue  # a fix for this problem already landed; don't let it stack
            if self._rule_matches(rule, name, args):
                self._apply_effect(rule)
                fired.append(rule["id"])
                self.state.fired_rules.append(rule["id"])
                if group:
                    self.state.fired_groups.append(group)
        return fired

    def _rule_matches(self, rule, name, args):
        trig = rule["trigger"]
        if trig.get("tool") != name:
            return False
        if "value_is" in trig and args.get("value") != trig["value_is"]:
            return False
        if "flag_contains" in trig:
            flag = _norm(args.get("flag", ""))
            if not any(_norm(kw) in flag for kw in trig["flag_contains"]):
                return False
        if "field_leq" in trig and not self._field_cmp(args, trig["field_leq"], "leq"):
            return False
        if "field_gt" in trig and not self._field_cmp(args, trig["field_gt"], "gt"):
            return False
        if "change_contains" in trig:
            cid = _norm(args.get("change_id", ""))
            if not any(_norm(kw) in cid for kw in trig["change_contains"]):
                return False
        blob = _norm(json.dumps(args, default=str))
        if "text_any" in trig and not any(_norm(kw) in blob for kw in trig["text_any"]):
            return False
        if "text_all" in trig:
            for group in trig["text_all"]:
                if not any(_norm(alt) in blob for alt in group):
                    return False
        for sig in rule.get("requires_prior", []):
            if sig not in self.state.tool_call_signatures:
                return False
        for sig in rule.get("requires_absent", []):
            if sig in self.state.tool_call_signatures:
                return False
        for kw in rule.get("requires_absent_flag", []):
            if any(_norm(kw) in _norm(f) for f in self.state.flags_set):
                return False
        return True

    def _field_cmp(self, args, spec, op):
        contains = _norm(spec["contains"])
        threshold = spec["value"]
        for key, val in self._flatten(args).items():
            if contains in _norm(key):
                try:
                    v = float(val)
                except (TypeError, ValueError):
                    continue
                if op == "leq" and v <= threshold:
                    return True
                if op == "gt" and v > threshold:
                    return True
        return False

    def _flatten(self, obj, out=None):
        out = {} if out is None else out
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    self._flatten(v, out)
                else:
                    out[k] = v
        elif isinstance(obj, list):
            for v in obj:
                self._flatten(v, out)
        return out

    def _apply_effect(self, rule):
        if rule.get("eng_weeks"):
            self.state.spend_eng_weeks(rule["eng_weeks"])
        effect = rule.get("effect") or {}
        kpis = effect.get("kpis") or {}
        rate = {k: v for k, v in kpis.items() if k in RATE_METRICS}
        count = {k: v for k, v in kpis.items() if k not in RATE_METRICS}
        if rate:
            self.state.apply_kpi_delta(rate, absolute=True)
        if count:
            self.state.apply_kpi_delta(count, absolute=False)
        if effect.get("unlocks_incident"):
            reveal_day = self.state.current_day + effect.get("reveal_after_days", 0)
            self.state.incidents_queued.append((effect["unlocks_incident"], reveal_day))
        self.state.clamp_kpis(RATE_METRICS)
