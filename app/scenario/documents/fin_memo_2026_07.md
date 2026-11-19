# FIN-MEMO-2026-07: Reverse auto-refund threshold to $50

**Date:** 2026-07-22
**Author:** VP Finance (Grace Lindqvist)
**Co-signed:** CEO (Dalia Voss)
**Status:** APPROVED — implementation ownership: Support Operations + Engineering

## Decision

Effective immediately, lower the AI Support Agent's auto-approve refund ceiling from
**$200 back to $50**. All refunds above $50 require manual review.

## Why

Fraud loss has risen sharply since the $200 ceiling shipped (PRD-2026-03). Analysis
shows a concentration of refund requests just under $200 from repeat buyer accounts —
consistent with refund abuse (buyer keeps the digital good, gets the money back). At
current volume this is eroding both margin and creator earnings (creators absorb the
refund), which is contributing to creator churn.

## Required implementation

1. Update **Refund Policy v3** to state the $50 auto-approve ceiling.
2. Confirm the Support Agent reloads the updated policy.
3. Risk to monitor refund distribution for 30 days post-change.

## Status check

As of this memo, Finance has approved. **Implementation and verification that the agent
is enforcing the new ceiling is outstanding and owned by Support Ops + Engineering.**
