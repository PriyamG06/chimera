#!/usr/bin/env python3
"""
CHIMERA synthetic event generator — seed chimera-001.

Deterministically builds chimera.db (SQLite) with ~50k events that encode the three
hidden root causes as REAL statistical signals, discoverable only by segmenting:

  rc1 (refund abuse):    refund events cluster in $150-200, auto_approved, repeat buyers,
                         because the support agent still enforces the stale $200 ceiling.
  rc2 (concentration):   after RN-2026-10 (2026-10-01) transactions concentrate on top
                         creators (Gini 0.58 -> ~0.81); new-creator cohort conversion -> ~0.
  rc3 (mobile checkout): after RN-2026-09 (2026-09-15) mobile+wallet success collapses,
                         hidden in the aggregate because desktop+card dominates volume.

Run:  python3 generate.py   (stdlib only; writes ./chimera.db)
Deterministic: same seed -> identical DB, which is what makes the benchmark reproducible.
"""

import sqlite3
import random
import os
from datetime import date, timedelta

SEED = "chimera-001"
RNG = random.Random(SEED)
DB_PATH = os.path.join(os.path.dirname(__file__), "chimera.db")

DAY0 = date(2026, 11, 16)            # "today" in the sim
HISTORY_DAYS = 90
START = DAY0 - timedelta(days=HISTORY_DAYS)
RN_CHECKOUT = date(2026, 9, 15)      # RN-2026-09 mobile-wallet regression begins
RN_RECO = date(2026, 10, 1)          # RN-2026-10 recommendation concentration begins

REGIONS = ["NA", "EU", "IN_SEA"]
PLATFORMS = ["desktop", "mobile_web"]
METHODS = ["card", "wallet"]

N_CREATORS = 1200
N_BUYERS = 8000
ABUSE_RING = 40                      # buyer accounts running refund abuse


def daterange_weight(d):
    # mild upward drift in traffic over the window
    return 1.0 + 0.3 * ((d - START).days / HISTORY_DAYS)


def build():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    con = sqlite3.connect(DB_PATH)
    c = con.cursor()

    c.executescript("""
    CREATE TABLE creators (
      creator_id INTEGER PRIMARY KEY,
      join_date TEXT,
      cohort TEXT,          -- 'established' | 'new'
      tier TEXT             -- 'top' | 'mid' | 'long_tail'
    );
    CREATE TABLE buyers (
      buyer_id INTEGER PRIMARY KEY,
      region TEXT,
      is_abuse INTEGER
    );
    CREATE TABLE events (
      event_id INTEGER PRIMARY KEY AUTOINCREMENT,
      ts TEXT,
      event_type TEXT,      -- 'purchase_attempt' | 'refund'
      creator_id INTEGER,
      buyer_id INTEGER,
      platform TEXT,
      payment_method TEXT,
      region TEXT,
      amount_usd REAL,
      status TEXT,          -- purchase: 'success'|'failed' ; refund: 'auto_approved'|'manual'
      note TEXT
    );
    """)

    # --- creators ---
    creators = []
    for cid in range(1, N_CREATORS + 1):
        # 15% joined recently (new cohort, mostly after RN_RECO era)
        if RNG.random() < 0.15:
            jd = START + timedelta(days=RNG.randint(55, HISTORY_DAYS))
            cohort = "new"
        else:
            jd = START - timedelta(days=RNG.randint(30, 400))
            cohort = "established"
        # tier: 5% top, 25% mid, 70% long tail
        r = RNG.random()
        tier = "top" if r < 0.05 else ("mid" if r < 0.30 else "long_tail")
        creators.append((cid, jd.isoformat(), cohort, tier))
    c.executemany("INSERT INTO creators VALUES (?,?,?,?)", creators)

    top = [cid for cid, _, _, t in creators if t == "top"]
    mid = [cid for cid, _, _, t in creators if t == "mid"]
    tail = [cid for cid, _, _, t in creators if t == "long_tail"]
    new_creators = [cid for cid, _, co, _ in creators if co == "new"]

    # --- buyers ---
    buyers = []
    abuse_ids = set(RNG.sample(range(1, N_BUYERS + 1), ABUSE_RING))
    for bid in range(1, N_BUYERS + 1):
        # IN_SEA is a large minority, heavy on mobile+wallet
        region = RNG.choices(REGIONS, weights=[0.4, 0.25, 0.35])[0]
        buyers.append((bid, region, 1 if bid in abuse_ids else 0))
    c.executemany("INSERT INTO buyers VALUES (?,?,?)", buyers)
    buyer_region = {bid: r for bid, r, _ in buyers}

    events = []

    def pick_creator(d):
        # rc2: before RN_RECO, spread across tiers; after, concentrate on top.
        if d < RN_RECO:
            pool = RNG.choices([top, mid, tail], weights=[0.20, 0.35, 0.45])[0]
        else:
            # concentration: top creators soak up most transactions
            pool = RNG.choices([top, mid, tail], weights=[0.65, 0.28, 0.07])[0]
        return RNG.choice(pool)

    def platform_method(region):
        # IN_SEA skews mobile+wallet; NA/EU skew desktop+card
        if region == "IN_SEA":
            plat = RNG.choices(PLATFORMS, weights=[0.35, 0.65])[0]
            meth = RNG.choices(METHODS, weights=[0.30, 0.70])[0]
        else:
            plat = RNG.choices(PLATFORMS, weights=[0.65, 0.35])[0]
            meth = RNG.choices(METHODS, weights=[0.75, 0.25])[0]
        return plat, meth

    def checkout_success(d, plat, meth, region):
        # rc3: mobile+wallet success collapses after RN_CHECKOUT
        base = 0.88
        if d >= RN_CHECKOUT and plat == "mobile_web" and meth == "wallet":
            return RNG.random() < 0.52     # ~40% error injection
        return RNG.random() < base

    # --- purchase attempts (~44k) ---
    n_days = HISTORY_DAYS
    for day in range(n_days):
        d = START + timedelta(days=day)
        n_today = int(480 * daterange_weight(d))
        for _ in range(n_today):
            bid = RNG.randint(1, N_BUYERS)
            region = buyer_region[bid]
            plat, meth = platform_method(region)
            cid = pick_creator(d)
            # rc2: new creators get almost no buyers after RN_RECO
            if d >= RN_RECO and cid in new_creators and RNG.random() < 0.92:
                cid = RNG.choice(top)      # buyer gets routed to an established creator instead
            amount = round(RNG.uniform(8, 240), 2)
            ok = checkout_success(d, plat, meth, region)
            events.append((d.isoformat(), "purchase_attempt", cid, bid, plat, meth,
                           region, amount, "success" if ok else "failed",
                           "checkout" if ok else "payment_validation_error"
                           if (plat == "mobile_web" and meth == "wallet" and d >= RN_CHECKOUT)
                           else "abandoned"))

    # --- refunds (~6k), rc1 signal ---
    for day in range(n_days):
        d = START + timedelta(days=day)
        n_ref = int(60 * daterange_weight(d))
        for _ in range(n_ref):
            # abuse ring: repeat refunds just under $200, auto-approved
            if RNG.random() < 0.35:
                bid = RNG.choice(list(abuse_ids))
                amount = round(RNG.uniform(150, 199), 2)   # clusters under $200
                status = "auto_approved"
                note = "auto <=200 per policy v3"
            else:
                bid = RNG.randint(1, N_BUYERS)
                amount = round(RNG.uniform(10, 199), 2)
                # still auto-approved up to 200 because the agent never got the $50 memo
                status = "auto_approved" if amount <= 200 else "manual"
                note = "auto <=200 per policy v3" if status == "auto_approved" else "manual review"
            cid = pick_creator(d)
            region = buyer_region[bid]
            events.append((d.isoformat(), "refund", cid, bid, None, None, region,
                           amount, status, note))

    RNG.shuffle(events)
    c.executemany(
        "INSERT INTO events (ts,event_type,creator_id,buyer_id,platform,payment_method,region,amount_usd,status,note) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)", events)
    con.commit()

    n_events = c.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    con.close()
    return n_events


if __name__ == "__main__":
    n = build()
    print(f"built {DB_PATH} with {n} events (seed {SEED})")
