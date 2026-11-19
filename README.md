# CHIMERA

**A product-judgment benchmark for frontier AI models.**

CHIMERA drops six frontier models into a single simulated company with a real problem and scores how each one investigates, prioritizes, and acts as its product manager. Every model runs the same 60-day gauntlet four times; results are reported as median ± standard deviation, so a lucky run cannot flatter a model.

**[Live dashboard →][dashboard]** | **[Full methodology (Substack) →][substack]**

---

## Leaderboard (n=4, median ± σ)

| Model | Score | Std Dev |
|-------|------:|--------:|
| **claude-opus-4-8** | **94.7** | **±1.9** |
| **gemini-3.8-flash** | **93.4** | **±5.8** |
| gpt-5.6-sol | 89.9 | ±4.3 |
| claude-haiku-4-5 | 84.0 | ±4.5 |
| gpt-5-mini | 77.6 | ±10.8 |
| gemini-2.5-flash-lite | 53.0 | ±19.0 |

The variance column is what matters. gpt-5-mini scored 93.5 on run 1 and 77.6 at the four-run median. flash-lite swung ±19.0. Opus leads on both median and consistency.

---

## What CHIMERA measures

Standard leaderboards test recall, math, and code generation. CHIMERA tests the judgment a product manager actually uses: the ambiguous, consequential calls made with incomplete information while stakeholders pull in different directions.

- **Does the model investigate before it acts?** Root causes are hidden across documents, a SQLite database, AI-agent logs, and stakeholder conversations. Any single source is misleading.
- **Does it segment instead of trusting the aggregate?** The headline numbers conceal the real story.
- **Does it pick the right first move?** A prioritization penalty fires when a model acts on a tactical symptom before the upstream cause.
- **Does it execute within real constraints?** A 12 engineering-week budget, a fraud-loss ceiling, a retention floor, and a hard safety rule.

---

## The gauntlet

Each model plays the newly-appointed senior PM of CHIMERA, a two-sided AI creator marketplace that is quietly failing while its vanity metric (creator signups) climbs. The mission: grow successful transactions 25% over 60 simulated days without breaching the guardrails. The model works only through tools (query data, read documents, inspect agent logs, interview users, message stakeholders, ship changes), across six stages:

1. **Investigate** — explore documents, history, and agent logs; find where the record and reality diverge.
2. **Root cause** — query the data, read tickets, interview users; segment the aggregates; separate correlation from causation.
3. **Decide** — allocate the 12 engineering-weeks across what to build, fix, or kill.
4. **Stakeholders** — align the people who challenge and sometimes mislead; defend priorities with evidence.
5. **Execute** — ship changes and respond to incidents as consequences land.
6. **Own the outcome** — review the metrics and decide whether to scale, iterate, roll back, or abandon.

Underneath sit three real root causes and three designed distractors:

- A stale refund policy an AI support agent still enforces, driving a fraud spike. The safety trap.
- A recommendation "win" that concentrated traffic onto top creators and starved the long tail. The biggest lever.
- A mobile-wallet checkout regression hidden inside an aggregate average. You only see it if you segment.
- Distractors the model must validate and reject: an architecture rewrite, a pricing cut, and a support-quality push.

The world is deterministic (seed `chimera-001`): roughly 55k synthetic events, 12 stakeholder personas, and a document set with built-in contradictions regenerate identically, so every model faces the same evidence.

---

## Dual scoring engine (100 points)

Every run is scored two independent ways:

| Component | Points | Dimensions |
|-----------|-------:|------------|
| Deterministic scorer | 52 | investigation (12), execution (20), outcomes (10), safety (10). Checked against the world's ground truth, no subjectivity. |
| Judge panel | 48 | root cause (15), product judgment (15), adaptability (10), stakeholder handling (8). |

The judge is a panel of three models, each scoring twice with the option order swapped, then medianed. The split isolates a specific failure mode: a model can score well on the judge (reads fluently, uses the right vocabulary) while failing the deterministic checks (wrong number, wrong action). An aggregate score hides that. Two numbers expose it.

---

## Multi-sample averaging (n=4)

Each model ran four independent times. Results are reported as median ± standard deviation.

A single run is not a measurement. It is one draw from the model's distribution. gpt-5-mini's 93.5 on its first run looked competitive until three more runs put the median at 77.6 with a ±10.8 swing. That one data point would have reversed a procurement decision.

---

## Architecture

```
Authored world (seed chimera-001)   one 60-day gauntlet, 6 stages
        |
        v
  Model runners (6 models x 4 runs, via tool-use)
        |
        v
  Dual scoring engine
    deterministic (52) + judge panel (48)
        |
        v
  Results store (24 run files)
        |
        v
  Next.js dashboard
```

---

## Running it

### Prerequisites

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r app/requirements.txt
```

The runner uses the OpenAI SDK and reads `OPENAI_API_KEY` (and optional `OPENAI_BASE_URL`, for any OpenAI-compatible gateway) from `config/.env` at the repo root (gitignored). Point it at whichever model endpoint you want to run.

### Single model, one run

```bash
cd app
python run.py claude-opus-4-8 --score
```

Writes `results/claude-opus-4-8.json` with the run transcript, the deterministic scorecard, and the judge scores.

### Named runs (for n>1 averaging)

```bash
python run.py gpt-5.6-sol --run-id run1 --score
python run.py gpt-5.6-sol --run-id run2 --score
python run.py gpt-5.6-sol --run-id run3 --score
```

Writes `results/gpt-5.6-sol_run1.json`, `_run2.json`, `_run3.json`.

### Full benchmark (all 6 models, multiple runs each)

```bash
cd app
bash run_batch.sh
```

Runs all models value-tier-first (cheaper models before expensive). One failure does not stop the rest.

### Leaderboard summary

```bash
cd app
python summarize.py
```

Reads every file in `results/`, groups by model slug, and prints median ± σ per model.

---

## Project structure

```
app/
  run.py          single-model gauntlet runner
  run_batch.sh    full benchmark (all models x N runs)
  summarize.py    leaderboard aggregator
  requirements.txt
  engine/         runner, environment, state, tools, scenario loader
  scenario/       world.yaml, documents, stakeholders, data, incidents, tickets
  scoring/
    deterministic.py   investigation / execution / outcomes / safety (52)
    judge.py           root cause / product judgment / adaptability / stakeholder (48)
    scorecard.py       combines both halves, applies hard-penalty overrides, clamps to 100
  results/        output JSON files (24: 6 models x 4 runs)
  tests/

dashboard/        Next.js dashboard (live at the link above)
```

---

## Adapting to your domain

CHIMERA's architecture is general. To run it against a different task domain:

1. Author a new world in `app/scenario/` (world.yaml, consequences.yaml, stakeholders, documents, data).
2. Update the deterministic scorer in `app/scoring/deterministic.py` with the correct answers for your task types.
3. Adjust the judge prompt and dimensions in `app/scoring/judge.py` for what matters in your domain.
4. Run with the same `run.py` + `run_batch.sh` + `summarize.py` pipeline.

The data schema is documented in [`app/scenario/data/SCHEMA.md`](app/scenario/data/SCHEMA.md).

---

## Eval & Error

CHIMERA is Project 1 of [Eval & Error][substack], a series that builds AI projects from scratch and documents what each one teaches. Season 1 theme: evaluations and model behavior.

Next: agent observability. What happens inside an agentic workflow when things go wrong, and how you would know in time to stop it.

[dashboard]: https://dashboard-two-pi-82enzhbgay.vercel.app
[substack]: https://evalanderror.substack.com/p/the-problem-with-ai-benchmarks
