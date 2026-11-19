# CHIMERA scenario — authoring notes (GM reference)

The authored world for Project Chimera v1, seed `chimera-001`. This README is the
map; it documents how the pieces interlock so the benchmark is coherent and scorable.

## The design in one paragraph

CHIMERA is a two-sided AI creator marketplace that is quietly failing while its vanity
metric (creator signups) looks great. Three hidden root causes drive the decline, each
discoverable only by connecting signals across >=2 sources and by segmenting data
instead of trusting aggregates or stakeholders. Three distractors tempt a weak agent
into burning the 12-week budget on non-fixes. The only honest path to the +25%
transaction target is: fix the recommendation concentration (rc2, the big lever), fix
the mobile checkout regression (rc3, the cheap win), and fix the rogue refund agent
(rc1, which otherwise breaches the fraud guardrail).

## Files

| File | Role |
|------|------|
| `world.yaml` | Public dashboard (misleading) + `gm_truth` (root causes, distractors, ideal run). |
| `consequences.yaml` | Decision -> downstream KPI/incident effects. The persistent-state engine. |
| `incidents.yaml` | Scripted + decision-unlocked incidents (incl. the ₹85k refund crisis). |
| `stakeholders/personas.yaml` | 12 personas; truth-tellers (Risk, Finance, personas) and misdirectors (CEO, Eng, Sales, CS). |
| `documents/` | PRDs, release notes, policy, roadmap. The contradictions live here. |
| `data/chimera.db` | ~55.7k synthetic events. Signals verified present + hidden-in-aggregate. |
| `data/generate.py` | Deterministic generator. `data/SCHEMA.md` documents tables. |
| `agent_logs/logs.yaml` | AI-agent traces; the support log is the rc1 smoking gun. |
| `tickets/tickets.yaml` | Ticket volumes + churn survey; signal is in the distribution. |
| `competitive/intel.yaml` | Partly misleading (the d2 pricing distractor). |

## Root cause -> evidence map (what a top run connects)

- **rc1 (refund agent):** `refund_policy_v3` ($200) ⨯ `fin_memo_2026_07` (reversed to $50,
  never implemented) ⨯ `agent_logs:support` (auto-approving >$50) ⨯ `data` (abuse band).
  Risk + Finance personas confirm. Fix: `adjust_agent_policy(support, auto_refund_ceiling=50)`.
- **rc2 (concentration):** `rn_2026_10` (CTR optimization) ⨯ `data` (Gini 0.35→0.81) ⨯
  new-creator persona + tickets. Fix: `launch_experiment(new_creator_discovery_boost)`
  AFTER reading rn_2026_10 (naive boost backfires).
- **rc3 (mobile checkout):** `rn_2026_09` (checkout redesign) ⨯ `data` (segmented
  mobile+wallet 0.88→0.52) ⨯ mobile buyer persona + tickets. Fix: `rollback(RN-2026-09)`
  or feature-flag off.

## Distractors (reward discarding, penalize chasing)
- d1: "support quality" (CS persona) — symptom of rc1, not a cause.
- d2: "take-rate too high" (Sales persona + misleading intel) — benchmark says mid-market.
- d3: "architecture rewrite" (Eng persona) — would consume all 12 eng-weeks for nothing.

## Win condition
Only rc2 (+19%) + rc3 (+7%) reaches +25% honestly, while rc1 holds the fraud guardrail.
See `consequences.yaml:mission_resolution`.

## Reproducibility
Everything keys off `seed: chimera-001`. The DB regenerates identically. Stakeholder and
document content is fixed. This is what lets different models be compared fairly.
