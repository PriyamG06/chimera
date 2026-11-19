# PRD-2026-03: Reduce support load via higher auto-refund threshold

**Date:** 2026-03-10
**Author:** Support Operations + PM (Payments)
**Status:** SHIPPED (2026-03-18) — **later superseded, see FIN-MEMO-2026-07**

## Problem

Support queue is overwhelmed. Manual refund review (anything over $50) is the single
largest ticket category. Resolution times are hurting CSAT.

## Decision

Raise the AI Support Agent's auto-approve refund ceiling from **$50 to $200**. Most
refunds fall under $200, so this removes ~70% of manual refund reviews.

## Risks flagged at the time

- Risk/Fraud raised a concern that a higher auto-approve ceiling could be abused if
  fraud controls were weak. Noted; accepted as low-probability at the time.

## Outcome

Shipped 2026-03-18. Reflected in Refund Policy v3. Support load dropped as expected.

> **Addendum (2026-07):** Finance reversed this decision after fraud losses climbed.
> See FIN-MEMO-2026-07. The reversal lowered the ceiling back to $50. Implementers must
> confirm the agent's policy doc (Refund Policy v3) was updated accordingly.
