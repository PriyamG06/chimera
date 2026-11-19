"""Tool surface for the agent under test.

Each tool is `fn(env, args) -> dict`. Read tools surface authored data; execution
tools record intent/mutate flags (the Environment applies consequences afterward).
TOOL_SCHEMAS is the OpenAI function-calling spec handed to the model.
"""
from __future__ import annotations
import sqlite3


def _persona_reply(env, args):
    personas = env.scenario.stakeholders()
    pid = args.get("persona_id")
    if pid not in personas:
        return {"error": f"unknown persona: {pid}"}
    responses = personas[pid]["responses"]
    msg = (args.get("message") or args.get("question") or "").lower()
    for topic, text in responses.items():
        if topic == "default":
            continue
        if topic.replace("_", " ") in msg or topic in msg:
            return {"persona": pid, "reply": text}
    return {"persona": pid, "reply": responses.get("default", "")}


def query_sql(env, args):
    q = args.get("query", "")
    try:
        con = sqlite3.connect(f"file:{env.scenario.db_path()}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        rows = [dict(r) for r in con.execute(q).fetchall()]
        con.close()
        env.state.query_log.append(q)
        return {"rows": rows[:500], "row_count": len(rows)}
    except sqlite3.Error as e:
        return {"error": str(e)}


def read_document(env, args):
    try:
        return {"body": env.scenario.read_document(args["doc_id"])}
    except KeyError as e:
        return {"error": str(e)}


def list_documents(env, args):
    return {"documents": env.scenario.list_documents()}


def read_tickets(env, args):
    t = env.scenario.tickets()
    flt = (args.get("filter") or "").lower()
    if not flt:
        return t
    samples = [s for s in t["sample_tickets"]
               if flt in s["category"].lower() or flt in s["text"].lower()]
    return {"volume_by_category": t["ticket_volume_by_category_last_30d"], "matching_tickets": samples}


def inspect_agent_logs(env, args):
    logs = env.scenario.agent_logs()
    aid = args.get("agent_id")
    if aid not in logs:
        return {"error": f"unknown agent: {aid}", "available": list(logs)}
    a = dict(logs[aid])
    # strip GM-only flags from traces before returning to the agent
    traces = [{k: v for k, v in tr.items() if k != "flag"} for tr in a.get("recent_traces", [])]
    return {"name": a["name"], "task_completion_rate": a["task_completion_rate"],
            "recent_traces": traces, "summary": a["summary"]}


def interview_user(env, args):
    return _persona_reply(env, args)


def message_stakeholder(env, args):
    return _persona_reply(env, args)


def list_stakeholders(env, args):
    return {"stakeholders": [{"id": pid, "role": p["role"]}
                             for pid, p in env.scenario.stakeholders().items()]}


def read_competitive_intel(env, args):
    intel = env.scenario.competitive()
    topic = (args.get("topic") or "").lower()
    if topic:
        for k, v in intel.items():
            if topic in k.lower():
                return {k: v}
    return intel


def _record_execution(env, kind, detail):
    env.state.decisions.append({"stage": env.state.stage, "kind": kind, "detail": detail})


def set_feature_flag(env, args):
    env.state.flags_set[args["flag"]] = args.get("value")
    _record_execution(env, "set_feature_flag", args)
    return {"ok": True, "flag": args["flag"], "value": args.get("value")}


def launch_experiment(env, args):
    _record_execution(env, "launch_experiment", args)
    return {"ok": True, "experiment": args.get("spec")}


def adjust_agent_policy(env, args):
    _record_execution(env, "adjust_agent_policy", args)
    return {"ok": True, "agent_id": args.get("agent_id"), "policy": args.get("policy")}


def rollback(env, args):
    _record_execution(env, "rollback", args)
    return {"ok": True, "rolled_back": args.get("change_id")}


def publish_incident_response(env, args):
    _record_execution(env, "publish_incident_response", {"text": args.get("text", "")})
    return {"ok": True, "published": True}


def _submit(kind):
    def fn(env, args):
        env.state.decisions.append({"stage": env.state.stage, "kind": kind,
                                    "content": args.get("text") or args.get("spec")})
        env.state.claimed_actions.append(kind)
        return {"ok": True, "submitted": kind}
    return fn


TOOLS = {
    "query_sql": query_sql,
    "read_document": read_document,
    "list_documents": list_documents,
    "read_tickets": read_tickets,
    "inspect_agent_logs": inspect_agent_logs,
    "interview_user": interview_user,
    "message_stakeholder": message_stakeholder,
    "list_stakeholders": list_stakeholders,
    "read_competitive_intel": read_competitive_intel,
    "set_feature_flag": set_feature_flag,
    "launch_experiment": launch_experiment,
    "adjust_agent_policy": adjust_agent_policy,
    "rollback": rollback,
    "publish_incident_response": publish_incident_response,
    "submit_diagnosis": _submit("submit_diagnosis"),
    "submit_roadmap": _submit("submit_roadmap"),
    "submit_outcome_report": _submit("submit_outcome_report"),
}

EXECUTION_TOOLS = {"set_feature_flag", "launch_experiment", "adjust_agent_policy",
                   "rollback", "publish_incident_response"}


def _fn(name, desc, props, required):
    return {"type": "function", "function": {
        "name": name, "description": desc,
        "parameters": {"type": "object", "properties": props, "required": required}}}


TOOL_SCHEMAS = [
    _fn("query_sql", "Run a read-only SQL query against the CHIMERA event store (SQLite). See the schema.",
        {"query": {"type": "string"}}, ["query"]),
    _fn("read_document", "Read a company document (PRD, release note, policy) by id.",
        {"doc_id": {"type": "string"}}, ["doc_id"]),
    _fn("list_documents", "List all available company documents.", {}, []),
    _fn("read_tickets", "Read support tickets + churn survey, optionally filtered by keyword/category.",
        {"filter": {"type": "string"}}, []),
    _fn("inspect_agent_logs", "Inspect an AI agent's execution traces (support, recommendation, shopping_assistant).",
        {"agent_id": {"type": "string"}}, ["agent_id"]),
    _fn("interview_user", "Ask a user persona (creator/buyer) a question.",
        {"persona_id": {"type": "string"}, "question": {"type": "string"}}, ["persona_id", "question"]),
    _fn("message_stakeholder", "Message an internal stakeholder (ceo, head_eng, head_risk, finance, ...).",
        {"persona_id": {"type": "string"}, "message": {"type": "string"}}, ["persona_id", "message"]),
    _fn("list_stakeholders", "List the internal stakeholders you can message.", {}, []),
    _fn("read_competitive_intel", "Read competitive intelligence, optionally by topic.",
        {"topic": {"type": "string"}}, []),
    _fn("set_feature_flag", "Set a product feature flag (mutates the product).",
        {"flag": {"type": "string"}, "value": {"type": ["boolean", "string", "number"]}}, ["flag", "value"]),
    _fn("launch_experiment", "Launch a product experiment/change. Pass a spec with a descriptive name.",
        {"spec": {"type": "object"}}, ["spec"]),
    _fn("adjust_agent_policy", "Change an AI agent's policy (e.g. support auto_refund_ceiling).",
        {"agent_id": {"type": "string"}, "policy": {"type": "object"}}, ["agent_id", "policy"]),
    _fn("rollback", "Roll back a prior change by id (e.g. a release RN-2026-09).",
        {"change_id": {"type": "string"}}, ["change_id"]),
    _fn("publish_incident_response", "Publish a response to an active incident.",
        {"text": {"type": "string"}}, ["text"]),
    _fn("submit_diagnosis", "Submit your evidence-backed diagnosis (stages 1-2 deliverable).",
        {"text": {"type": "string"}}, ["text"]),
    _fn("submit_roadmap", "Submit your prioritized roadmap + tradeoffs (stage 3 deliverable).",
        {"spec": {"type": "object"}}, ["spec"]),
    _fn("submit_outcome_report", "Submit your final outcome report (stage 6 deliverable).",
        {"text": {"type": "string"}}, ["text"]),
]
