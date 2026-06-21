"""
SAARTHI — Stage 5: interactive layer
  A. WHAT-IF simulator feed  — event archetype locations + per-dow cells (JS re-optimizes live)
  B. CASCADE total (done right) — direct + Σ derived spillover impact per corridor
  C. URGENCY tiers            — cause -> deploy-now / within-1h / pre-positioned
Extends dashboard_data.json in place.
"""
import json, re, numpy as np, pandas as pd
from pathlib import Path
from collections import defaultdict

import os
ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("SAARTHI_OUT", str(ROOT / "outputs")))
df=pd.read_csv(OUT/"incidents_enriched.csv",low_memory=False,parse_dates=["t_event"])
df["date"]=pd.to_datetime(df["date"])
risk=pd.read_csv(OUT/"risk_by_dow.csv")
dd=json.load(open(OUT/"dashboard_data.json"))

def hav(la,lo,la2,lo2):
    R=6371;p1,p2=np.radians(la),np.radians(la2)
    dphi=np.radians(la2-la);dl=np.radians(lo2-lo)
    x=np.sin(dphi/2)**2+np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2
    return 2*R*np.arcsin(np.sqrt(x))

# ============================================================================= #
# A. WHAT-IF — event archetypes with a representative location + impact bump
# ============================================================================= #
VENUE={"chinnaswamy|cricket|ipl|rcb":"Cricket / IPL (Chinnaswamy)",
 "rathotsava|utsava|uthsava|car festival|temple|jatre|palakki":"Religious procession",
 "metro":"Metro construction",
 "nhai|bwssb|kride|k.?ride|white ?tapping|road work|works|construction":"Infrastructure works",
 "protest|dharna|bandh|rally":"Protest / rally","vip|cm |minister|convoy":"VIP movement"}
def arch(s):
    s=str(s).lower()
    for p,n in VENUE.items():
        if re.search(p,s): return n
    return "Other"
p=df[df.event_type=="planned"].copy(); p["a"]=p.description.apply(arch)
archetypes=[]
for name,g in p.groupby("a"):
    if name=="Other": continue
    archetypes.append({"name":name,"lat":round(float(g.lat.median()),5),
        "lon":round(float(g.lon.median()),5),"bump":round(float(g.impact_min.median()),0),
        "events":int(len(g)),"p90_hold":int(np.percentile(g.exp_clearance_min,90))})
archetypes=sorted(archetypes,key=lambda x:-x["bump"])

# compact per-dow cells for the browser optimizer (lat,lon,w=[7 dow weights])
piv=(risk.pivot_table(index=["lat","lon"],columns="dow",values="exp_impact",fill_value=0)
        .reset_index())
sim_cells=[{"lat":round(r["lat"],5),"lon":round(r["lon"],5),
            "w":[round(float(r.get(d,0)),1) for d in range(7)]} for _,r in piv.iterrows()]

# ============================================================================= #
# B. CASCADE TOTAL — direct + derived spillover impact (not eyeballed)
#    cascaded[A] = Σ_B  observed_cascades(A->B) × mean_impact_per_incident(B)
# ============================================================================= #
u=df[df.event_type=="unplanned"].sort_values("t_event").reset_index(drop=True)
valid=set(n["corridor"] for n in dd["network"]["nodes"])
uu=u[u.corridor.isin(valid)].reset_index(drop=True)
t=uu.t_event.values.astype("datetime64[s]").astype(np.int64).astype(float)
la,lo,cor=uu.lat.values,uu.lon.values,uu.corridor.values
trans=defaultdict(int)
for i in range(len(uu)):
    j=i+1
    while j<len(uu) and (t[j]-t[i])<=90*60:
        if cor[j]!=cor[i] and hav(la[i],lo[i],la[j],lo[j])<=4.0: trans[(cor[i],cor[j])]+=1
        j+=1
mean_imp=uu.groupby("corridor").impact_min.mean().to_dict()
direct=uu.groupby("corridor").impact_min.sum().to_dict()
cascade={}
for a in valid:
    casc=sum(c*mean_imp.get(b,0) for (aa,b),c in trans.items() if aa==a)
    d0=direct.get(a,0)
    cascade[a]={"direct":round(d0/1000,1),"cascaded":round(casc/1000,1),
                "total":round((d0+casc)/1000,1),
                "amplify":round((d0+casc)/d0,2) if d0 else 1.0}

# ============================================================================= #
# C. URGENCY TIERS — operational cadence by cause
#    red = fast-escalating (respond now) · amber = slow-building · green = known/planned
# ============================================================================= #
TIER={
 "accident":"red","protest":"red","public_event":"red","congestion":"red","vip_movement":"red",
 "procession":"amber","water_logging":"amber","tree_fall":"amber","construction":"amber","fog / low visibility":"amber",
 "vehicle_breakdown":"std","pot_holes":"std","road_conditions":"std","others":"std","debris":"std",
}
LABEL={"red":"Deploy ≤15 min","amber":"Deploy ≤1 hr","green":"Pre-position (known)","std":"Standard"}
# planned archetypes that are known in advance -> green
PLANNED_GREEN={"Metro construction","Infrastructure works","VIP movement"}

dd["scenario"]={"archetypes":archetypes,"cells":sim_cells,
                "K":8,"reach_km":2.5,"minsep_km":1.8}
dd["cascade"]=cascade
dd["urgency"]={"tier":TIER,"label":LABEL,"planned_green":list(PLANNED_GREEN)}
json.dump(dd,open(OUT/"dashboard_data.json","w"),indent=1,default=str)

print("A. SCENARIO archetypes (event -> location bump):")
for a in archetypes: print(f"  {a['name']:<28} @({a['lat']},{a['lon']})  +{a['bump']:.0f} congestion-min  hold≤{a['p90_hold']}m  ({a['events']} hist)")
print(f"   sim cells exported: {len(sim_cells)}")
print("\nB. CASCADE total (top by amplification):")
for a,v in sorted(cascade.items(),key=lambda x:-x[1]['amplify'])[:6]:
    print(f"  {a:<16} direct {v['direct']}k + cascaded {v['cascaded']}k = {v['total']}k  (×{v['amplify']} system amplification)")
print("\nC. URGENCY tiers:")
for tier in ["red","amber","std"]:
    print(f"  {LABEL[tier]:<22}: {', '.join(c for c,t in TIER.items() if t==tier)}")
print("  Pre-position (known)  :", ", ".join(PLANNED_GREEN))
print("\nExtended dashboard_data.json")
