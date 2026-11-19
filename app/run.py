#!/usr/bin/env python3
"""Run one model through the CHIMERA gauntlet and write results/<model>.json.

Usage:
  python run.py <model_id> [--budget N] [--stages s1,s2,...]
Loads config/.env (proxy key) automatically.
"""
import sys
import os
import json
import argparse
from pathlib import Path

APP = Path(__file__).resolve().parent
sys.path.insert(0, str(APP))


def load_env():
    env_path = APP.parents[2] / "config" / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--budget", type=int, default=25)
    ap.add_argument("--stages", default=None, help="comma-separated subset of stages")
    ap.add_argument("--score", action="store_true", help="score the run with the judge panel")
    ap.add_argument("--run-id", default=None, help="run identifier appended to output filename, e.g. run1")
    args = ap.parse_args()

    load_env()
    from engine.scenario import Scenario
    from engine.environment import Environment
    from engine.runner import Runner

    scenario = Scenario(APP / "scenario")
    env = Environment(scenario)
    stages = args.stages.split(",") if args.stages else None
    runner = Runner(env, args.model, max_calls_per_stage=args.budget, stages=stages)
    result = runner.run()

    out_dir = APP / "results"
    out_dir.mkdir(exist_ok=True)
    slug = args.model.replace('/', '_')
    suffix = f"_{args.run_id}" if args.run_id else ""
    out_path = out_dir / f"{slug}{suffix}.json"

    # Always persist the run + deterministic score BEFORE the (expensive, failable) judge,
    # so a budget/network failure never discards a completed run.
    from scoring import scorecard
    result["scorecard"] = scorecard.score_deterministic(env.state, scenario)
    out_path.write_text(json.dumps(result, indent=2, default=str))

    judge_error = None
    if args.score:
        try:
            result["scorecard"] = scorecard.score_run(env.state, scenario, transcript=result["transcript"])
            out_path.write_text(json.dumps(result, indent=2, default=str))
        except Exception as e:  # judge panel can fail on proxy budget/network
            judge_error = e

    print(f"model: {result['model']}")
    print(f"stages: {[(s['stage'], s['tool_calls']) for s in result['stages']]}")
    print(f"eng_weeks_spent: {result['eng_weeks_spent']}")
    print(f"tool signatures: {env.state.tool_call_signatures[:20]}")
    print(f"final_kpis: {result['final_kpis']}")
    print(f"decisions: {[(d['stage'], d['kind']) for d in env.state.decisions]}")
    sc = result["scorecard"]
    if "total" in sc:
        print(f"SCORE: {sc['total']}/100  (deterministic {sc['comparison']['deterministic_total']} | "
              f"judge {sc['comparison']['judge_total']} | penalties {sc['penalties']})")
    else:
        print(f"DETERMINISTIC: {sc['deterministic']['subtotal']}/52 (judge not run)")
    if judge_error:
        print(f"JUDGE SKIPPED: {judge_error}")
    print(f"written: {out_path}")


if __name__ == "__main__":
    main()
