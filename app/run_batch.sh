#!/usr/bin/env bash
# Run the full CHIMERA benchmark: all six models x 3 runs, scored, each saved independently.
# Resilient — one model/run failing does not stop the others. Each writes
# results/<model>_run{N}.json with at least a deterministic score before the judge runs.
set -u
cd "$(dirname "$0")"
PY=.venv/bin/python
N=3

# Value tier first (cheaper) so a budget pause leaves us the most results.
MODELS=(
  claude-haiku-4-5
  gpt-5-mini
  gemini-2.5-flash-lite
  gemini-3.8-flash
  gpt-5.6-sol
  claude-opus-4-8
)

for m in "${MODELS[@]}"; do
  for i in $(seq 1 $N); do
    echo "===== $m  run $i/$N ====="
    $PY run.py "$m" --budget 18 --score --run-id "run${i}" || echo "!! $m run${i} failed (continuing)"
    echo
  done
done

echo "===== LEADERBOARD ====="
$PY summarize.py
