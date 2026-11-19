# CHIMERA data environment — schema

`query_sql(query)` runs read-only SQL against `chimera.db` (SQLite, ~55.7k rows,
deterministic for seed chimera-001). The agent is shown this schema but NOT the signals;
it must segment the data to find them.

## Tables

### events (~55,700 rows)
| column | type | notes |
|--------|------|-------|
| event_id | INTEGER | pk |
| ts | TEXT | ISO date, spans ~2026-08-18 to 2026-11-16 |
| event_type | TEXT | `purchase_attempt` or `refund` |
| creator_id | INTEGER | fk -> creators |
| buyer_id | INTEGER | fk -> buyers |
| platform | TEXT | `desktop` or `mobile_web` (null for refunds) |
| payment_method | TEXT | `card` or `wallet` (null for refunds) |
| region | TEXT | `NA`, `EU`, `IN_SEA` |
| amount_usd | REAL | |
| status | TEXT | purchase: `success`/`failed`; refund: `auto_approved`/`manual` |
| note | TEXT | e.g. `payment_validation_error`, `auto <=200 per policy v3` |

### creators (1,200 rows)
| column | type | notes |
|--------|------|-------|
| creator_id | INTEGER | pk |
| join_date | TEXT | ISO date |
| cohort | TEXT | `established` or `new` |
| tier | TEXT | `top` / `mid` / `long_tail` |

### buyers (8,000 rows)
| column | type | notes |
|--------|------|-------|
| buyer_id | INTEGER | pk |
| region | TEXT | `NA`/`EU`/`IN_SEA` |
| is_abuse | INTEGER | GM-only ground truth; keep queryable for scoring, not advertised to agent |

## Reference dates (knowable from release notes, not from the data itself)
- `2026-09-15` — RN-2026-09 checkout redesign (rc3 begins)
- `2026-10-01` — RN-2026-10 recommendation optimization (rc2 begins)

## Example queries that reveal each root cause
```sql
-- rc3: segment conversion, don't trust the aggregate
SELECT platform, payment_method, AVG(status='success')
FROM events WHERE event_type='purchase_attempt' AND ts>='2026-09-15'
GROUP BY platform, payment_method;

-- rc2: transaction concentration by creator tier after the reco change
SELECT c.tier, COUNT(*) FROM events e JOIN creators c ON e.creator_id=c.creator_id
WHERE e.event_type='purchase_attempt' AND e.status='success' AND e.ts>='2026-10-01'
GROUP BY c.tier;

-- rc1: refund abuse band + repeat offenders
SELECT buyer_id, COUNT(*) n FROM events
WHERE event_type='refund' AND amount_usd BETWEEN 150 AND 199
GROUP BY buyer_id HAVING n>=5;
```

## Rebuild
`python3 generate.py` regenerates `chimera.db` identically from the seed.
