"""Tests for engine.runner.Runner — the stage-driving tool-calling loop.

Uses a scripted fake client (no network) so the loop logic is tested in isolation.
"""
from pathlib import Path
import json
import pytest
from engine.scenario import Scenario
from engine.environment import Environment
from engine.runner import Runner

SCENARIO_DIR = Path(__file__).resolve().parents[1] / "scenario"


# --- minimal OpenAI-shaped fakes ---
class _Fn:
    def __init__(self, name, args): self.name = name; self.arguments = json.dumps(args)


class _ToolCall:
    def __init__(self, i, name, args): self.id = f"c{i}"; self.type = "function"; self.function = _Fn(name, args)


class _Msg:
    def __init__(self, content="", tool_calls=None): self.content = content; self.tool_calls = tool_calls


class _Resp:
    def __init__(self, msg): self.choices = [type("C", (), {"message": msg})]


class FakeClient:
    """Returns scripted responses in order; records calls."""
    def __init__(self, script):
        self._script = list(script)
        self.calls = 0
        self.chat = type("Chat", (), {"completions": self})()

    def create(self, **kwargs):
        self.calls += 1
        return _Resp(self._script.pop(0) if self._script else _Msg(content="done"))


@pytest.fixture
def env():
    return Environment(Scenario(SCENARIO_DIR))


def test_runner_executes_a_tool_call_the_model_emits(env):
    script = [_Msg(tool_calls=[_ToolCall(1, "query_sql", {"query": "SELECT COUNT(*) AS n FROM events"})]),
              _Msg(content="stage done, no more tools")]
    r = Runner(env, "fake-model", client=FakeClient(script), max_calls_per_stage=5, stages=["investigate"])
    r.run()
    assert "SELECT COUNT(*) AS n FROM events" in env.state.query_log


def test_stage_ends_when_model_stops_calling_tools(env):
    script = [_Msg(content="nothing to do here")]
    r = Runner(env, "fake-model", client=FakeClient(script), max_calls_per_stage=5, stages=["investigate"])
    result = r.run()
    assert result["stages"][0]["tool_calls"] == 0


def test_per_stage_budget_caps_runaway_loops(env):
    # a client that ALWAYS wants another tool call
    class Loopy(FakeClient):
        def create(self, **kwargs):
            self.calls += 1
            return _Resp(_Msg(tool_calls=[_ToolCall(self.calls, "list_documents", {})]))
    r = Runner(env, "fake-model", client=Loopy([]), max_calls_per_stage=3, stages=["investigate"])
    result = r.run()
    assert result["stages"][0]["tool_calls"] == 3


def test_runner_walks_all_six_stages_by_default(env):
    r = Runner(env, "fake-model", client=FakeClient([]), max_calls_per_stage=1)
    result = r.run()
    assert len(result["stages"]) == 6
    assert env.state.stage == 6


def test_result_captures_final_kpis(env):
    r = Runner(env, "fake-model", client=FakeClient([]), max_calls_per_stage=1, stages=["investigate"])
    result = r.run()
    assert result["final_kpis"]["successful_transactions"] == 10600


# --- cross-provider compatibility (learned from the first batch) ---
def test_tool_result_message_includes_function_name():
    # Gemini's backend rejects a tool result without the function name.
    tc = _ToolCall(1, "query_sql", {"query": "x"})
    msg = Runner._tool_result_msg(tc, {"rows": []})
    assert msg["name"] == "query_sql"
    assert msg["tool_call_id"] == "c1"
    assert msg["role"] == "tool"


def test_stage_boundary_after_tool_results_gets_a_model_turn_bridge(env):
    # Gemini rejects two consecutive user turns (tool results -> next stage prompt).
    r = Runner(env, "m", client=FakeClient([]), stages=["x"])
    messages = [{"role": "user", "content": "a"},
                {"role": "tool", "tool_call_id": "c1", "name": "q", "content": "{}"}]
    r._ensure_model_turn(messages)
    assert messages[-1]["role"] == "assistant"


def test_no_bridge_when_last_turn_is_already_assistant(env):
    r = Runner(env, "m", client=FakeClient([]), stages=["x"])
    messages = [{"role": "assistant", "content": "done"}]
    r._ensure_model_turn(messages)
    assert len(messages) == 1
