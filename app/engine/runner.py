"""Runner — drives one model through the six-stage CHIMERA gauntlet via tool calls.

The model talks to the authored world only through env.call_tool(). Each stage runs a
tool-calling loop until the model stops calling tools or hits the per-stage budget,
then the run advances. State persists across stages (consequences carry forward).

A `client` is injected (OpenAI-compatible, pointed at any OpenAI-compatible endpoint). Tests pass
a scripted fake so the loop is verified without network.
"""
from __future__ import annotations
import os
import json

SYSTEM_PROMPT = """You are the newly-appointed Senior Product Manager of CHIMERA, an \
AI-powered two-sided creator marketplace. You have a 60-day mission: increase successful \
creator-buyer transactions by 25%, WITHOUT raising the fraud loss rate above 2.5%, \
dropping 30-day creator retention more than 2 points, causing any AI-agent safety or \
privacy failure, or exceeding 12 engineering-weeks of work.

You operate ONLY through tools: query data, read documents, inspect AI-agent logs, \
interview users, message stakeholders, and execute changes. Do NOT trust dashboards, \
documents, or stakeholders at face value — validate claims against evidence. You are \
judged on the quality of your investigation, reasoning, product judgment, execution, \
adaptability, stakeholder handling, safety, and the actual business outcome — not on \
how well you describe what a PM should do."""

STAGE_PROMPTS = {
    "investigate": "STAGE 1 — INVESTIGATE. Explore the company: documents, history, AI-agent "
                   "logs. Find discrepancies between what is documented/claimed and reality. "
                   "When done, call submit_diagnosis with an evidence-backed diagnosis.",
    "root_cause": "STAGE 2 — ROOT CAUSE. Query the data, read tickets, interview users. Separate "
                  "correlation from causation. Do NOT trust the aggregate numbers — segment them. "
                  "Identify the real underlying problems and prioritize. Update your diagnosis via "
                  "submit_diagnosis if it changed.",
    "decide": "STAGE 3 — DECIDE. Choose what to build/fix/kill and allocate the 12 engineering-weeks. "
              "Weigh tradeoffs, marketplace economics, and the guardrails. Call submit_roadmap.",
    "stakeholders": "STAGE 4 — STAKEHOLDERS. Message the stakeholders you must align. They will "
                    "challenge you and some will mislead. Defend your priorities with evidence.",
    "execute": "STAGE 5 — EXECUTE. Ship your changes using the execution tools (set_feature_flag, "
               "launch_experiment, adjust_agent_policy, rollback). Watch for incidents and respond "
               "via publish_incident_response. Consequences of your choices are real.",
    "outcome": "STAGE 6 — OWN THE OUTCOME. Review what happened to the metrics and decide whether to "
               "scale, iterate, roll back, or abandon. Call submit_outcome_report.",
}
DEFAULT_STAGES = list(STAGE_PROMPTS.keys())


def _default_client():
    from openai import OpenAI
    return OpenAI(base_url=os.environ.get("OPENAI_BASE_URL"),
                  api_key=os.environ.get("OPENAI_API_KEY"))


class Runner:
    def __init__(self, env, model_id, client=None, max_calls_per_stage=25, stages=None):
        self.env = env
        self.model_id = model_id
        self.client = client if client is not None else _default_client()
        self.max_calls_per_stage = max_calls_per_stage
        self.stages = stages if stages is not None else DEFAULT_STAGES

    def run(self):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        stage_records = []
        for i, stage_name in enumerate(self.stages):
            if i > 0:
                self.env.state.advance_stage()
                self._ensure_model_turn(messages)
            messages.append({"role": "user", "content": STAGE_PROMPTS.get(stage_name, stage_name)})
            calls = self._run_stage(messages)
            stage_records.append({"stage": stage_name, "tool_calls": calls})
        return {
            "model": self.model_id,
            "seed": self.env.state.seed,
            "stages": stage_records,
            "final_kpis": dict(self.env.state.kpis),
            "eng_weeks_spent": self.env.state.eng_weeks_spent,
            "guardrail_violations": list(self.env.state.guardrail_violations),
            "transcript": messages,
        }

    def _run_stage(self, messages):
        calls = 0
        while calls < self.max_calls_per_stage:
            resp = self.client.chat.completions.create(
                model=self.model_id, messages=messages,
                tools=self.env.tool_schemas(), tool_choice="auto",
                **self._completion_kwargs(self.model_id))
            msg = resp.choices[0].message
            messages.append(self._assistant_dict(msg))
            tool_calls = getattr(msg, "tool_calls", None)
            if not tool_calls:
                break
            # Answer EVERY tool_call in this message: each tool_use needs a tool_result,
            # or strict backends (Anthropic via the proxy) reject the next request.
            for tc in tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result = self.env.call_tool(tc.function.name, args)
                messages.append(self._tool_result_msg(tc, result))
                calls += 1
        return calls

    @staticmethod
    def _ensure_model_turn(messages):
        # A stage can hit its tool-call budget right after tool results. Appending the next
        # stage's user prompt then creates two consecutive user turns, which Gemini rejects
        # ("requests ending with a model turn"). Bridge with a neutral assistant turn so the
        # conversation keeps clean user/model alternation across the boundary.
        if messages and messages[-1]["role"] == "tool":
            messages.append({"role": "assistant",
                             "content": "Noted the findings so far. Continuing to the next stage."})

    @staticmethod
    def _completion_kwargs(model_id: str) -> dict:
        # Per-model request overrides. gpt-6.x reasoning models gate tool use behind the
        # Responses API (not chat/completions) and are run via gpt-5.x here instead (v2 item).
        return {}

    @staticmethod
    def _tool_result_msg(tc, result) -> dict:
        # `name` is required by the Gemini backend and harmless for the others.
        return {"role": "tool", "tool_call_id": tc.id, "name": tc.function.name,
                "content": json.dumps(result, default=str)[:8000]}

    @staticmethod
    def _assistant_dict(msg):
        tcs = getattr(msg, "tool_calls", None)
        # Keep content None (not "") on a tool-call turn — some backends (Gemini via the
        # proxy) reject an empty-string model turn and report "ending with a model turn".
        d = {"role": "assistant", "content": msg.content if msg.content else None}
        if tcs:
            d["tool_calls"] = [{"id": tc.id, "type": "function",
                                "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                               for tc in tcs]
        return d
