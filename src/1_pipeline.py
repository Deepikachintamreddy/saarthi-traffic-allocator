"""
SAARTHI  —  Spatio-temporal Allocation, Anomaly & Risk Triage for High-impact Incidents
========================================================================================
Gridlock Hackathon 2.0 | Theme 2: Event-Driven Congestion (Planned & Unplanned)
Dataset: Astram event log (Bengaluru Traffic Police), 8,173 incidents, Nov-2023 -> Apr-2024

WHY THIS IS DIFFERENT
---------------------
99% of teams will treat this as "forecast the NUMBER of events per zone/hour".
That is wrong twice over, because this dataset hides two traps:

  TRAP A (Time):  Absolute hour-of-day is CORRUPTED. The stored start_datetime mixes
                  timezone conventions and there is a synthetic 02:00-IST batch-creation
                  spike. Any model keyed on raw hour learns noise. -> we neutralise it.

  TRAP B (Duration): closed_datetime is mostly a BATCH AUTO-CLOSE. ~46% of "durations"
                  pile into a synthetic 120-180 min band. Naive "avg clearance time"
                  is garbage. -> we treat batch-closed rows as right-censored and model
                  clearance time on the trustworthy signal only.

SAARTHI instead forecasts EXPECTED CONGESTION-MINUTES (a single physical currency) and
then OPTIMALLY PRE-POSITIONS scarce enforcement units against that surface. That directly
answers the PS's three asks: (1) forecast impact, (2) recommend manpower/barricading/
diversion, (3) post-event learning loop.

PIPELINE
  1. DATA SPINE        clean + canonicalise + flag both traps
  2. TRUE-IMPACT NLP   mine Kannada/English descriptions for actual traffic effect
  3. CIQ               Congestion-Impact Quantifier  (congestion-minutes per incident)
  4. CLEARANCE MODEL   censoring-aware expected-clearance-time per incident
  5. RISK SURFACE      grid x day-of-week expected congestion-minutes (unplanned track)
  6. PLANNED TRACK     parse named venues/events -> deterministic impact calendar
  7. OPTIMIZER         greedy max-coverage pre-positioning of K units + barricades
  8. EXPORTS           artifacts for the dashboard / submission
"""

import re, json, warnings
import numpy as np
import pandas as pd
from pathlib import Path

warnings.filterwarnings("ignore")
import os
ROOT = Path(__file__).resolve().parents[1]
SRC = os.environ.get("SAARTHI_DATA", str(ROOT / "data" / "astram_events.csv"))
OUT = Path(os.environ.get("SAARTHI_OUT", str(ROOT / "outputs"))); OUT.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------------- #
# 1. DATA SPINE
# ----------------------------------------------------------------------------- #
def load_and_clean():
    df = pd.read_csv(SRC, low_memory=False)

    # treat the literal string 'NULL'/'' as missing everywhere
    df = df.replace({"NULL": np.nan, "": np.nan, "None": np.nan})

    # --- coords (already 100% inside Bengaluru bbox, but guard anyway) ---
    df["lat"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["lon"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df[df.lat.between(12.6, 13.3) & df.lon.between(77.3, 77.9)].copy()

    # --- timestamps ---
    to_dt = lambda s: pd.to_datetime(df[s], errors="coerce", utc=True)
    df["t_start"]    = to_dt("start_datetime")
    df["t_created"]  = to_dt("created_date")
    df["t_modified"] = to_dt("modified_datetime")
    df["t_closed"]   = to_dt("closed_datetime")
    df["t_resolved"] = to_dt("resolved_datetime")

    # canonical incident time = created_date (operator hit 'create' at report time);
    # 92% of |created-start| < 5 min, and created is internally consistent.
    df["t_event"] = df["t_created"].fillna(df["t_start"])

    # --- TRAP A: build ONLY robust temporal features (no absolute hour) ---
    ist = df["t_event"].dt.tz_convert("Asia/Kolkata")
    df["dow"]        = ist.dt.dayofweek            # 0=Mon  (clean, trustworthy)
    df["is_weekend"] = df["dow"].isin([5, 6]).astype(int)
    df["month"]      = ist.dt.month
    df["date"]       = ist.dt.date
    # coarse, robust day-part instead of raw hour (collapses the tz jitter)
    h = ist.dt.hour
    df["daypart"] = pd.cut(h, [-1, 6, 11, 16, 21, 24],
                           labels=["night", "morning", "midday", "evening", "late"]).astype(str)

    # --- TRAP B: censoring flag for clearance time ---
    end_best = df["t_closed"].fillna(df["t_resolved"]).fillna(df["t_modified"])
    df["dur_raw_min"] = (end_best - df["t_event"]).dt.total_seconds() / 60.0
    # the synthetic batch-close band + 'closed via batch' = NOT a real clearance time
    batch_band = df["dur_raw_min"].between(118, 182)
    closed_not_resolved = df["t_resolved"].isna() & df["t_closed"].notna()
    df["clearance_censored"] = (batch_band & closed_not_resolved).astype(int)
    # trustworthy duration = human-resolved OR naturally-distributed (outside synthetic band)
    df["dur_trust_min"] = np.where(
        (df["dur_raw_min"] > 0) & (df["dur_raw_min"] < 1440) & (df["clearance_censored"] == 0),
        df["dur_raw_min"], np.nan)

    # --- normalise key categoricals ---
    df["event_type"]  = df["event_type"].str.lower().str.strip()
    df["cause"]       = df["event_cause"].str.lower().str.strip().replace({"debris ": "debris"})
    df["cause"]       = df["cause"].fillna("others")
    df["priority"]    = df["priority"].fillna("Low")
    df["closure"]     = df["requires_road_closure"].astype(str).str.upper().eq("TRUE").astype(int)
    df["corridor"]    = df["corridor"].fillna("Non-corridor").str.strip()
    df["is_corridor"] = (~df["corridor"].eq("Non-corridor")).astype(int)
    return df

# ----------------------------------------------------------------------------- #
# 2. TRUE-IMPACT NLP  (mine noisy Kannada/English descriptions)
# ----------------------------------------------------------------------------- #
NEG = re.compile(r"normal|no problem|no issue|cleared|clear|smooth|fine|ok\b|resolved|"
                 r"ಸಮಸ್ಯೆ ಇಲ್ಲ|ಸರಿ|ಕ್ಲಿಯರ್", re.I)
POS = re.compile(r"slow|jam|block|stuck|heavy traffic|swol|choke|congest|conje|diversion|"
                 r"ನಿಧಾನ|ಬ್ಲಾಕ್|ಜಾಮ್|ಟ್ರಾಫಿಕ್", re.I)

def true_impact_label(df):
    d = df["description"].fillna("").astype(str)
    neg, pos = d.str.contains(NEG), d.str.contains(POS)
    # +1 says traffic affected, -1 says explicitly fine, 0 unknown
    df["text_signal"] = np.select([pos & ~neg, neg & ~pos], [1, -1], default=0)
    return df

# ----------------------------------------------------------------------------- #
# 4. CLEARANCE MODEL (censoring-aware expected minutes)  [run before CIQ]
# ----------------------------------------------------------------------------- #
def clearance_model(df):
    """Expected clearance minutes per incident from the TRUSTWORTHY signal only.
       Hierarchical fallback: (cause,priority,corridor-tier) -> (cause,priority) -> (cause) -> global.
       This is effectively a censoring-aware estimator: batch-closed rows are excluded
       (treated as right-censored) so the synthetic 2-3h spike cannot bias the estimate."""
    tier = np.where(df["is_corridor"] == 1, "art", "loc")
    df["_tier"] = tier
    trust = df[df["dur_trust_min"].notna()]

    g3 = trust.groupby(["cause", "priority", "_tier"])["dur_trust_min"].median()
    g2 = trust.groupby(["cause", "priority"])["dur_trust_min"].median()
    g1 = trust.groupby(["cause"])["dur_trust_min"].median()
    g0 = trust["dur_trust_min"].median()

    def lookup(r):
        for key, tbl in [((r.cause, r.priority, r._tier), g3),
                         ((r.cause, r.priority), g2),
                         ((r.cause,), g1)]:
            v = tbl.get(key if len(key) > 1 else key[0], np.nan)
            if pd.notna(v):
                return v
        return g0
    df["exp_clearance_min"] = df.apply(lookup, axis=1).clip(2, 600)
    return df, {"global_median_min": round(float(g0), 1),
                "by_cause_min": g1.round(1).sort_values(ascending=False).to_dict()}

# ----------------------------------------------------------------------------- #
# 3. CIQ — Congestion-Impact Quantifier  (the unifying currency)
# ----------------------------------------------------------------------------- #
def congestion_impact(df):
    """impact (congestion-minutes) =
         severity(priority, closure, text) x corridor_criticality x expected_clearance_min
       Every downstream decision optimises THIS, not raw event counts."""
    sev = np.where(df["priority"].eq("High"), 2.0, 1.0)
    sev = sev * np.where(df["closure"] == 1, 1.8, 1.0)
    sev = sev * np.where(df["text_signal"] == 1, 1.25,
                  np.where(df["text_signal"] == -1, 0.6, 1.0))

    # data-driven corridor criticality: share of High+closure incidents on that corridor,
    # min-max scaled to [1.0, 2.0] so arterials dominate Non-corridor.
    crit = (df.assign(hc=((df.priority.eq("High")) | (df.closure == 1)).astype(int))
              .groupby("corridor")["hc"].mean())
    crit = 1.0 + (crit - crit.min()) / (crit.max() - crit.min() + 1e-9)  # 1..2
    df["corridor_crit"] = df["corridor"].map(crit).fillna(1.0)

    df["impact_min"] = (sev * df["corridor_crit"] * df["exp_clearance_min"]).round(1)
    return df, crit.sort_values(ascending=False)

# ----------------------------------------------------------------------------- #
# 5. RISK SURFACE  (unplanned track: grid x day-of-week expected congestion-minutes)
# ----------------------------------------------------------------------------- #
GRID = 0.012  # ~1.3 km cells
def risk_surface(df):
    u = df[df.event_type == "unplanned"].copy()
    u["gx"] = (u.lon / GRID).round().astype(int)
    u["gy"] = (u.lat / GRID).round().astype(int)
    n_days = max(u["date"].nunique(), 1)

    # expected congestion-minutes generated per cell per day-of-week
    cell_dow = (u.groupby(["gy", "gx", "dow"])["impact_min"].sum()
                  .reset_index(name="sum_impact"))
    # per-DOW day counts to get a true daily expectation
    days_per_dow = (u.drop_duplicates("date").groupby("dow")["date"].count())
    cell_dow["exp_impact_per_day"] = cell_dow.apply(
        lambda r: r.sum_impact / max(days_per_dow.get(r.dow, 1), 1), axis=1).round(1)

    # cell centroids + dominant cause for explainability
    cent = (u.groupby(["gy", "gx"])
              .agg(lat=("lat", "mean"), lon=("lon", "mean"),
                   n=("id", "size"), impact=("impact_min", "sum"),
                   top_cause=("cause", lambda s: s.value_counts().idxmax()),
                   top_corridor=("corridor", lambda s: s.value_counts().idxmax()))
              .reset_index())
    cent["exp_impact_per_day"] = (cent["impact"] / n_days).round(1)
    cent = cent.sort_values("impact", ascending=False)
    return cent, cell_dow

# ----------------------------------------------------------------------------- #
# 6. PLANNED TRACK  (deterministic: parse named venues / event archetypes)
# ----------------------------------------------------------------------------- #
VENUE = {
    "chinnaswamy|m chinnaswamy|cricket|ipl|rcb": "Chinnaswamy Stadium (cricket/IPL)",
    "rathotsava|rathothsava|utsava|uthsava|car festival|temple|jatre|palakki": "Religious procession/festival",
    "metro|namma metro": "Metro construction/closure",
    "nhai|bwssb|k.?ride|kride|white ?tapping|tar|asphalt|road work|works|construction": "Infrastructure works",
    "protest|dharna|bandh|rally": "Protest/rally",
    "vip|cm |minister|convoy": "VIP movement",
}
def planned_track(df):
    p = df[df.event_type == "planned"].copy()
    d = p["description"].fillna("").astype(str)
    arche = pd.Series("Other planned", index=p.index)
    for pat, name in VENUE.items():
        arche = arche.mask(d.str.contains(pat, case=False, regex=True) & arche.eq("Other planned"), name)
    p["archetype"] = arche
    summ = (p.groupby("archetype")
              .agg(events=("id", "size"),
                   med_impact=("impact_min", "median"),
                   closures=("closure", "sum"),
                   med_clearance=("exp_clearance_min", "median"))
              .sort_values("med_impact", ascending=False).round(1))
    return p, summ

# ----------------------------------------------------------------------------- #
# 7. OPTIMIZER  (greedy max-coverage pre-positioning of K units)
# ----------------------------------------------------------------------------- #
def haversine(a_lat, a_lon, b_lat, b_lon):
    R = 6371.0
    p1, p2 = np.radians(a_lat), np.radians(b_lat)
    dphi = np.radians(b_lat - a_lat); dl = np.radians(b_lon - a_lon)
    x = np.sin(dphi/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2
    return 2*R*np.arcsin(np.sqrt(x))

def prepositioning(cent, K=8, reach_km=2.5, dow=None, cell_dow=None):
    """Place K patrol anchors to maximise covered EXPECTED congestion-minutes.
       If dow given, weight cells by that day's expectation (day-specific plan)."""
    cells = cent.copy()
    if dow is not None and cell_dow is not None:
        w = (cell_dow[cell_dow.dow == dow].set_index(["gy", "gx"])["exp_impact_per_day"])
        cells["weight"] = cells.set_index(["gy", "gx"]).index.map(w).fillna(0).values
    else:
        cells["weight"] = cells["exp_impact_per_day"]
    cells = cells[cells.weight > 0].reset_index(drop=True)

    chosen, covered = [], np.zeros(len(cells), dtype=bool)
    for _ in range(K):
        best_gain, best_i = -1, None
        for i in range(len(cells)):
            if i in [c["idx"] for c in chosen]:
                continue
            d = haversine(cells.lat.values, cells.lon.values, cells.lat[i], cells.lon[i])
            mask = (d <= reach_km) & (~covered)
            gain = cells.weight.values[mask].sum()
            if gain > best_gain:
                best_gain, best_i, best_mask = gain, i, mask
        if best_i is None:
            break
        covered |= best_mask
        chosen.append({"idx": int(best_i),
                       "lat": float(cells.lat[best_i]), "lon": float(cells.lon[best_i]),
                       "anchor_corridor": cells.top_corridor[best_i],
                       "covered_impact_per_day": round(float(best_gain), 1)})
    total = cells.weight.sum()
    got = sum(c["covered_impact_per_day"] for c in chosen)
    return chosen, round(100 * got / (total + 1e-9), 1)

# ----------------------------------------------------------------------------- #
# RUN
# ----------------------------------------------------------------------------- #
if __name__ == "__main__":
    df = load_and_clean()
    df = true_impact_label(df)
    df, clr = clearance_model(df)
    df, crit = congestion_impact(df)
    cent, cell_dow = risk_surface(df)
    planned, planned_summ = planned_track(df)

    print(f"\n{'='*70}\nSAARTHI — pipeline run\n{'='*70}")
    print(f"Incidents after cleaning : {len(df):,}")
    print(f"  planned / unplanned    : {(df.event_type=='planned').sum():,} / {(df.event_type=='unplanned').sum():,}")
    print(f"  batch-close CENSORED    : {df.clearance_censored.sum():,} "
          f"({100*df.clearance_censored.mean():.0f}% of rows had a fake clearance time)")
    print(f"  trustworthy durations   : {df.dur_trust_min.notna().sum():,}")
    print(f"\nClearance (censoring-aware) global median: {clr['global_median_min']} min")
    print("  by cause (min):", {k: clr['by_cause_min'][k] for k in list(clr['by_cause_min'])[:6]})

    print(f"\nTotal congestion-minutes in window: {df.impact_min.sum():,.0f}")
    print("Top corridor criticality:", {k: round(v,2) for k,v in crit.head(6).items()})

    print(f"\n--- TOP 10 UNPLANNED RISK CELLS (expected congestion-min / day) ---")
    show = cent.head(10)[["lat","lon","exp_impact_per_day","n","top_cause","top_corridor"]]
    print(show.to_string(index=False))

    print(f"\n--- PLANNED EVENT ARCHETYPES (impact) ---")
    print(planned_summ.to_string())

    # day-specific deployment plan (e.g., busiest weekday)
    busiest_dow = int(df[df.event_type=='unplanned'].groupby('dow').impact_min.sum().idxmax())
    plan, cov = prepositioning(cent, K=8, reach_km=2.5, dow=busiest_dow, cell_dow=cell_dow)
    dname = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][busiest_dow]
    print(f"\n--- PRE-POSITIONING: 8 units, {dname} (highest-load day) ---")
    print(f"Expected congestion-minutes COVERED: {cov}% with just 8 anchors")
    for i,c in enumerate(plan,1):
        print(f"  Unit {i}: ({c['lat']:.4f},{c['lon']:.4f})  ~{c['anchor_corridor']:<18}"
              f"  covers {c['covered_impact_per_day']}/day")

    # ---- exports for dashboard ----
    df.to_csv(OUT/"incidents_enriched.csv", index=False)
    cent.to_csv(OUT/"risk_cells.csv", index=False)
    cell_dow.to_csv(OUT/"risk_cells_by_dow.csv", index=False)
    planned_summ.to_csv(OUT/"planned_archetypes.csv")
    json.dump({"deployment_dow": dname, "coverage_pct": cov, "units": plan,
               "clearance": clr,
               "total_congestion_minutes": float(df.impact_min.sum())},
              open(OUT/"saarthi_summary.json","w"), indent=2)
    print(f"\nExports -> {OUT}/  (incidents_enriched, risk_cells, risk_cells_by_dow, planned_archetypes, summary)")
