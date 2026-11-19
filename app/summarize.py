#!/usr/bin/env python3
"""Leaderboard across n-run result files.

Groups results/{model}_run{N}.json by model slug, aggregates across runs,
and prints median + mean ± σ per model. Falls back gracefully to single-run
files with no _run suffix (legacy or one-off runs).
"""
import json
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, stdev

RESULTS = Path(__file__).resolve().parent / "results"


def _stem_to_slug(stem: str) -> str:
    m = re.match(r"^(.+)_run\d+$", stem)
    return m.group(1) if m else stem


def _fmt_stat(vals: list, fmt: str = ".1f") -> str:
    if not vals:
        return "—"
    med = median(vals)
    if len(vals) == 1:
        return f"{med:{fmt}}"
    mu = mean(vals)
    sigma = stdev(vals)
    return f"{med:{fmt}} ({mu:{fmt}}±{sigma:{fmt}})"


def _num(vals: list, fmt: str = ".1f") -> tuple:
    """Return (median_str, mean±σ_str) for a column that wants them split."""
    if not vals:
        return "—", "—"
    med = f"{median(vals):{fmt}}"
    if len(vals) == 1:
        return med, "—"
    mu = mean(vals)
    sigma = stdev(vals)
    return med, f"{mu:{fmt}}±{sigma:{fmt}}"


def main():
    groups: dict[str, list[dict]] = defaultdict(list)

    for f in sorted(RESULTS.glob("*.json")):
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        slug = _stem_to_slug(f.stem)
        sc = d.get("scorecard", {})
        k = d.get("final_kpis", {})
        groups[slug].append({
            "model": d.get("model", slug),
            "total": sc.get("total"),
            "det": sc.get("deterministic", {}).get("subtotal"),
            "judge": sc.get("comparison", {}).get("judge_total"),
            "calib": sc.get("judge", {}).get("calibration_mean_spread"),
            "txns": k.get("successful_transactions"),
            "fraud": k.get("fraud_loss_rate"),
            "eng_wk": d.get("eng_weeks_spent"),
        })

    rows = []
    for slug, runs in groups.items():
        def nums(key):
            return [r[key] for r in runs if r[key] is not None]

        totals = nums("total")
        rows.append({
            "model": runs[0]["model"],
            "n": len(runs),
            "totals": totals,
            "med_total": median(totals) if totals else -1,
            "det": nums("det"),
            "judge": nums("judge"),
            "calib": nums("calib"),
            "txns": nums("txns"),
            "fraud": nums("fraud"),
            "eng_wk": nums("eng_wk"),
        })

    rows.sort(key=lambda r: r["med_total"], reverse=True)

    w = max((len(r["model"]) for r in rows), default=5)

    # Header
    hdr = (f"{'model':<{w}}  {'n':>2}  {'total (med / mean±σ)':>22}  "
           f"{'det':>5}  {'judge':>5}  {'txns':>6}  {'fraud':>7}  {'eng':>4}")
    print(hdr)
    print("-" * len(hdr))

    for r in rows:
        t_med, t_ms = _num(r["totals"])
        d_med, _ = _num(r["det"], ".0f")
        j_med, _ = _num(r["judge"], ".1f")
        c_med, _ = _num(r["calib"], ".2f")
        tx_med, _ = _num(r["txns"], ".0f")
        fr_med, _ = _num(r["fraud"], ".4f")
        e_med, _ = _num(r["eng_wk"], ".0f")

        total_col = f"{t_med} / {t_ms}" if t_ms != "—" else t_med
        print(f"{r['model']:<{w}}  {r['n']:>2}  {total_col:>22}  "
              f"{d_med:>5}  {j_med:>5}  {tx_med:>6}  {fr_med:>7}  {e_med:>4}")


if __name__ == "__main__":
    main()
