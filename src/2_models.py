"""
SAARTHI — Stage 2: ML models + consolidated dashboard export
Builds on incidents_enriched.csv produced by saarthi_pipeline.py
  A. Spatio-temporal risk forecaster  (HistGBM, time-validated, vs baseline)
  B. Clearance-time quantile model     (P50 / P90, censoring-aware)
  C. Per-day-of-week deployment plans   (greedy max-coverage)
  D. Planned-event calendar engine      (plan_for_date)
  E. dashboard_data.json                (single feed the UI consumes)
"""
import json, numpy as np, pandas as pd, re
from pathlib import Path
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error

import os
ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("SAARTHI_OUT", str(ROOT / "outputs")))
df = pd.read_csv(OUT/"incidents_enriched.csv", low_memory=False, parse_dates=["t_event"])
df["date"] = pd.to_datetime(df["date"])
GRID = 0.012
df["gx"] = (df.lon/GRID).round().astype(int)
df["gy"] = (df.lat/GRID).round().astype(int)
u = df[df.event_type=="unplanned"].copy()

# ----------------------------------------------------------------------------- #
# A. SPATIO-TEMPORAL RISK FORECASTER
#    unit of analysis = (active cell, calendar date); target = congestion-minutes
#    that day. Most days are 0 -> model learns WHERE and WHEN risk concentrates.
# ----------------------------------------------------------------------------- #
def build_risk_model(u):
    cells = u.groupby(["gy","gx"]).agg(lat=("lat","mean"),lon=("lon","mean"),
              hist_n=("id","size"), hist_impact=("impact_min","sum"),
              crit=("corridor_crit","mean")).reset_index()
    cells = cells[cells.hist_n>=5]                       # stable cells only
    dates = pd.date_range(u.date.min(), u.date.max(), freq="D")
    # full (cell x date) panel
    panel = (cells.assign(key=1).merge(pd.DataFrame({"date":dates,"key":1}), on="key")
                  .drop(columns="key"))
    daily = (u.groupby(["gy","gx","date"])["impact_min"].sum().reset_index(name="y"))
    panel = panel.merge(daily, on=["gy","gx","date"], how="left").fillna({"y":0})
    panel["dow"]=panel.date.dt.dayofweek; panel["month"]=panel.date.dt.month
    panel["is_weekend"]=panel.dow.isin([5,6]).astype(int)
    panel["hist_rate"]=panel.hist_impact/panel.hist_n

    feats=["lat","lon","dow","month","is_weekend","hist_n","hist_rate","crit"]
    cut = u.date.max()-pd.Timedelta(days=30)
    tr,te = panel[panel.date<=cut], panel[panel.date>cut]
    m = HistGradientBoostingRegressor(max_depth=6, learning_rate=0.08,
                                      max_iter=400, l2_regularization=1.0)
    m.fit(tr[feats], tr.y)
    te=te.copy(); te["pred"]=np.clip(m.predict(te[feats]),0,None)
    # OPERATIONAL METRIC: capture rate. Each held-out day, rank cells by predicted
    # risk, deploy to the top 20% — what % of that day's ACTUAL congestion-minutes
    # do we catch? Average over the 30 unseen days. Compare to cell-mean baseline.
    cellmean=tr.groupby(["gy","gx"]).y.mean()
    te["cm"]=te.set_index(["gy","gx"]).index.map(cellmean).fillna(0).values
    def capture(col):
        caps=[]
        for _,g in te.groupby("date"):
            if g.y.sum()==0: continue
            k=max(1,int(0.20*len(g)))
            top=g.nlargest(k,col)
            caps.append(top.y.sum()/g.y.sum())
        return round(100*np.mean(caps),1)
    cap_model, cap_base = capture("pred"), capture("cm")
    mae_m=mean_absolute_error(te.y,te.pred)
    panel["pred"]=np.clip(m.predict(panel[feats]),0,None)
    risk = (panel.groupby(["gy","gx","lat","lon","dow"]).pred.mean()
                 .reset_index(name="exp_impact"))
    return risk, {"capture_top20pct_model":cap_model,"capture_top20pct_baseline":cap_base,
                  "model_MAE":round(mae_m,1),"n_cells":int(cells.shape[0]),"test_days":30}

risk, risk_metrics = build_risk_model(u)

# ----------------------------------------------------------------------------- #
# B. CLEARANCE QUANTILE MODEL  (how long to hold a unit)  — censoring-aware
# ----------------------------------------------------------------------------- #
def build_clearance(df):
    t = df[df.dur_trust_min.notna() & (df.dur_trust_min<600)].copy()
    cause_e = {c:i for i,c in enumerate(sorted(t.cause.unique()))}
    t["ce"]=t.cause.map(cause_e); t["pe"]=(t.priority=="High").astype(int)
    X=t[["ce","pe","closure","corridor_crit","is_corridor"]]
    cut=t.t_event.max()-pd.Timedelta(days=30)
    tr=t[t.t_event<=cut]; te=t[t.t_event>cut]
    out={}
    for q in [0.5,0.9]:
        m=HistGradientBoostingRegressor(loss="quantile",quantile=q,max_iter=300,max_depth=5)
        m.fit(tr[X.columns],tr.dur_trust_min); out[q]=m
    p50=out[0.5].predict(te[X.columns]); 
    mae=mean_absolute_error(te.dur_trust_min,p50)
    base=mean_absolute_error(te.dur_trust_min,np.full(len(te),tr.dur_trust_min.median()))
    # export P50/P90 by cause (what the dashboard shows)
    grid=pd.DataFrame([{"cause":c,"ce":cause_e[c],"pe":1,"closure":0,
                        "corridor_crit":1.5,"is_corridor":1} for c in cause_e])
    grid["P50_min"]=out[0.5].predict(grid[X.columns]).round(0)
    grid["P90_min"]=out[0.9].predict(grid[X.columns]).round(0)
    return grid.sort_values("P90_min",ascending=False), \
           {"P50_MAE":round(mae,1),"baseline_MAE":round(base,1),
            "lift_pct":round(100*(base-mae)/base,1)}, out, cause_e, list(X.columns)

clr_tbl, clr_metrics, clr_models, cause_e, clr_cols = build_clearance(df)

# ----------------------------------------------------------------------------- #
# C. DEPLOYMENT — greedy max-coverage per day-of-week
# ----------------------------------------------------------------------------- #
def haversine(la,lo,la2,lo2):
    R=6371; p1,p2=np.radians(la),np.radians(la2)
    dphi=np.radians(la2-la); dl=np.radians(lo2-lo)
    x=np.sin(dphi/2)**2+np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2
    return 2*R*np.arcsin(np.sqrt(x))

def deploy(risk,dow,K=8,reach=2.5,minsep=1.8):
    c=risk[(risk.dow==dow)&(risk.exp_impact>0)].reset_index(drop=True)
    if len(c)==0: return [],0.0
    cov=np.zeros(len(c),bool); chosen=[]
    for _ in range(K):
        bg,bi,bm=-1,None,None
        for i in range(len(c)):
            if i in [x["i"] for x in chosen]: continue
            # min-separation: keep anchors spread across the city, not stacked
            if any(haversine(c.lat[i],c.lon[i],c.lat[x["i"]],c.lon[x["i"]])<minsep
                   for x in chosen): continue
            d=haversine(c.lat.values,c.lon.values,c.lat[i],c.lon[i])
            mask=(d<=reach)&(~cov); g=c.exp_impact.values[mask].sum()
            if g>bg: bg,bi,bm=g,i,mask
        if bi is None: break
        cov|=bm; chosen.append({"i":int(bi),"lat":round(float(c.lat[bi]),5),
            "lon":round(float(c.lon[bi]),5),"covers":round(float(bg),1)})
    tot=c.exp_impact.sum(); got=sum(x["covers"] for x in chosen)
    for x in chosen: x.pop("i")
    return chosen, round(100*got/(tot+1e-9),1)

plans={}; 
for d in range(7):
    units,cov=deploy(risk,d); plans[d]={"units":units,"coverage_pct":cov}
risk.round({"lat":5,"lon":5,"exp_impact":1}).to_csv(OUT/"risk_by_dow.csv",index=False)

# ----------------------------------------------------------------------------- #
# D. PLANNED-EVENT CALENDAR ENGINE
# ----------------------------------------------------------------------------- #
VENUE={"chinnaswamy|cricket|ipl|rcb":"Chinnaswamy cricket/IPL",
 "rathotsava|utsava|uthsava|car festival|temple|jatre|palakki":"Religious procession",
 "metro":"Metro construction","nhai|bwssb|kride|k.?ride|white ?tapping|road work|works|construction":"Infrastructure works",
 "protest|dharna|bandh|rally":"Protest/rally","vip|cm |minister|convoy":"VIP movement"}
def archetype(s):
    s=str(s).lower()
    for p,n in VENUE.items():
        if re.search(p,s): return n
    return "Other planned"
p=df[df.event_type=="planned"].copy(); p["arch"]=p.description.apply(archetype)
planned_summ=(p.groupby("arch").agg(events=("id","size"),med_impact=("impact_min","median"),
    p90_clear=("exp_clearance_min",lambda s:round(np.percentile(s,90),0)),
    closures=("closure","sum")).sort_values("med_impact",ascending=False).round(1)
    .reset_index())

def plan_for_date(month,day,dow):
    """Calendar engine: given a date, return base deployment + any planned-event uplift."""
    base=plans[dow]
    # planned events historically on that calendar day
    hits=p[(p.t_event.dt.month==month)&(p.t_event.dt.day==day)]
    extra=[{"archetype":a,"impact":round(float(g.impact_min.sum()),1),
            "hold_min":int(np.percentile(g.exp_clearance_min,90))}
           for a,g in hits.groupby("arch")] if len(hits) else []
    return {"base_units":base["units"],"base_coverage":base["coverage_pct"],
            "planned_uplift":extra}

# ----------------------------------------------------------------------------- #
# E. EXPORT consolidated feed
# ----------------------------------------------------------------------------- #
heat=(risk.groupby(["lat","lon"]).exp_impact.mean().reset_index()
          .query("exp_impact>0").round({"lat":5,"lon":5,"exp_impact":1}))
# top hotspots with context
hot=(u.groupby(["gy","gx"]).agg(lat=("lat","mean"),lon=("lon","mean"),n=("id","size"),
        impact=("impact_min","sum"),cause=("cause",lambda s:s.value_counts().idxmax()),
        corridor=("corridor",lambda s:s.value_counts().idxmax())).reset_index()
        .sort_values("impact",ascending=False).head(15).round({"lat":5,"lon":5}))
ndays=df.date.nunique()
hot["per_day"]=(hot.impact/ndays).round(1)

dash={
 "meta":{"incidents":int(len(df)),"planned":int((df.event_type=='planned').sum()),
         "unplanned":int((df.event_type=='unplanned').sum()),
         "window":f"{df.date.min().date()} to {df.date.max().date()}",
         "total_congestion_minutes":int(df.impact_min.sum()),"days":int(ndays),
         "censored_pct":round(100*df.clearance_censored.mean(),1)},
 "risk_metrics":risk_metrics,"clearance_metrics":clr_metrics,
 "heat":heat.to_dict("records"),
 "hotspots":hot[["lat","lon","n","per_day","cause","corridor"]].to_dict("records"),
 "deploy_by_dow":plans,
 "clearance_by_cause":clr_tbl[["cause","P50_min","P90_min"]].to_dict("records"),
 "planned_archetypes":planned_summ.to_dict("records"),
 "dow_load":{d:round(float(u[u.dow==d].impact_min.sum()),0) for d in range(7)},
 "corridor_load":(u.groupby("corridor").impact_min.sum().sort_values(ascending=False)
                   .head(10).round(0).to_dict()),
}
json.dump(dash,open(OUT/"dashboard_data.json","w"),indent=1,default=str)

print("RISK MODEL  ",risk_metrics)
print("CLEARANCE   ",clr_metrics)
print("\nClearance P50/P90 by cause:\n",clr_tbl[["cause","P50_min","P90_min"]].head(8).to_string(index=False))
print("\nDeployment coverage by DOW:",{['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][d]:plans[d]['coverage_pct'] for d in range(7)})
print("\nplan_for_date demo (Feb 12 = Chinnaswamy match day, dow=Mon):")
print(json.dumps(plan_for_date(2,12,0)["planned_uplift"],indent=1))
print("\nExported dashboard_data.json")
