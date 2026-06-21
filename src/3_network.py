"""
SAARTHI — Stage 3: the differentiators
  A. Corridor SPILLOVER network  (data-mined propagation A -> nearby B)
  B. DIVERSION recommender        (parallel corridors NOT in the blast radius)
  C. Marginal COVERAGE curve      (how many units to hit X%)
  D. ABNORMAL-DAY detector        (unannounced-event early warning)
Extends dashboard_data.json in place.
"""
import json, numpy as np, pandas as pd
from pathlib import Path

import os
ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("SAARTHI_OUT", str(ROOT / "outputs")))
df = pd.read_csv(OUT/"incidents_enriched.csv", low_memory=False, parse_dates=["t_event"])
df["date"] = pd.to_datetime(df["date"])
u = df[df.event_type=="unplanned"].sort_values("t_event").copy()

# corridor centroids (named arterials only — these are the network nodes)
nodes = (u[u.corridor!="Non-corridor"].groupby("corridor")
           .agg(lat=("lat","mean"),lon=("lon","mean"),
                load=("impact_min","sum"),n=("id","size")).reset_index())
nodes = nodes[nodes.n>=20].reset_index(drop=True)
valid = set(nodes.corridor)

def hav(la,lo,la2,lo2):
    R=6371;p1,p2=np.radians(la),np.radians(la2)
    dphi=np.radians(la2-la);dl=np.radians(lo2-lo)
    x=np.sin(dphi/2)**2+np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2
    return 2*R*np.arcsin(np.sqrt(x))

# centroid distance matrix between corridors (for parallel/adjacency)
cd = nodes.set_index("corridor")[["lat","lon"]]
def dist(a,b): return hav(cd.lat[a],cd.lon[a],cd.lat[b],cd.lon[b])

# ----------------------------------------------------------------------------- #
# A. SPILLOVER:  for each incident, count follow-ons within T<=90min & <=4km on a
#    DIFFERENT corridor. Compare observed A->B transitions to chance -> lift.
# ----------------------------------------------------------------------------- #
uu = u[u.corridor.isin(valid)].reset_index(drop=True)
t = uu.t_event.values.astype("datetime64[s]").astype(np.int64)
la, lo, cor = uu.lat.values, uu.lon.values, uu.corridor.values
T, Dkm = 90*60, 4.0
from collections import defaultdict
trans = defaultdict(int)
j0 = 0
for i in range(len(uu)):
    j = i+1
    while j < len(uu) and (t[j]-t[i])<=T:
        if cor[j]!=cor[i]:
            d = hav(la[i],lo[i],la[j],lo[j])
            if d<=Dkm:
                trans[(cor[i],cor[j])] += 1
        j += 1
# base rate of each corridor as a target
tgt_base = pd.Series(cor).value_counts(normalize=True).to_dict()
edges=[]
src_tot=defaultdict(int)
for (a,b),c in trans.items(): src_tot[a]+=c
for (a,b),c in trans.items():
    if c<3: continue
    obs = c/max(src_tot[a],1)
    lift = obs/ (tgt_base.get(b,1e-9))
    edges.append({"src":a,"dst":b,"count":int(c),"lift":round(lift,2)})
edges = sorted(edges,key=lambda e:-e["lift"])

# blast radius per corridor = top-3 downstream by lift
blast=defaultdict(list)
for e in edges:
    if len(blast[e["src"]])<3 and e["lift"]>1.1:
        blast[e["src"]].append({"corridor":e["dst"],"lift":e["lift"]})

# ----------------------------------------------------------------------------- #
# B. DIVERSION:  for a corridor A, recommend the 2 nearest corridors that are
#    NOT in A's blast radius (i.e. won't also be choking) -> safe reroute.
# ----------------------------------------------------------------------------- #
diversion={}
for a in valid:
    bset = {b["corridor"] for b in blast.get(a,[])}
    cand = [(b, dist(a,b)) for b in valid if b!=a and b not in bset]
    cand = sorted(cand,key=lambda x:x[1])[:2]
    diversion[a] = [{"corridor":c,"km":round(d,1)} for c,d in cand if d<8]

# ----------------------------------------------------------------------------- #
# C. MARGINAL COVERAGE CURVE  (greedy 1..15 anchors, busiest day)
# ----------------------------------------------------------------------------- #
dd = json.load(open(OUT/"dashboard_data.json"))
risk_cells = pd.read_csv(OUT/"risk_cells.csv")  # has lat,lon,impact, exp_impact_per_day
busiest = int(max(dd["dow_load"], key=lambda k: dd["dow_load"][k]))
# use per-day expected impact as weights
cells = risk_cells.rename(columns={"exp_impact_per_day":"w"})[["lat","lon","w"]]
cells = cells[cells.w>0].reset_index(drop=True)
def coverage_curve(cells,Kmax=15,reach=2.5,minsep=2.0):
    cov=np.zeros(len(cells),bool); chosen=[]; curve=[]
    for k in range(Kmax):
        bg,bi,bm=-1,None,None
        for i in range(len(cells)):
            if i in chosen: continue
            # min-separation: don't stack anchors
            if any(hav(cells.lat[i],cells.lon[i],cells.lat[c],cells.lon[c])<minsep for c in chosen):
                continue
            d=hav(cells.lat.values,cells.lon.values,cells.lat[i],cells.lon[i])
            mask=(d<=reach)&(~cov); g=cells.w.values[mask].sum()
            if g>bg: bg,bi,bm=g,i,mask
        if bi is None: break
        cov|=bm; chosen.append(bi)
        curve.append(round(100*cells.w.values[cov].sum()/cells.w.sum(),1))
    return curve, [ {"lat":round(float(cells.lat[i]),5),"lon":round(float(cells.lon[i]),5)} for i in chosen]
curve, dispersed = coverage_curve(cells)
# units needed to hit thresholds
def units_for(p): 
    for k,v in enumerate(curve,1):
        if v>=p: return k
    return len(curve)

# ----------------------------------------------------------------------------- #
# D. ABNORMAL-DAY DETECTOR  (z-score vs same-day-of-week baseline)
# ----------------------------------------------------------------------------- #
daily = u.groupby("date").agg(impact=("impact_min","sum"),n=("id","size")).reset_index()
daily["dow"]=daily.date.dt.dayofweek
mu=daily.groupby("dow").impact.transform("mean"); sd=daily.groupby("dow").impact.transform("std")
daily["z"]=((daily.impact-mu)/sd).round(2)
top_ab = daily.sort_values("z",ascending=False).head(6)
# what was happening that day (dominant cause + any planned event)
pl = df[df.event_type=="planned"].copy()
def context(dt):
    day=u[u.date==dt]; cause=day.cause.value_counts().idxmax() if len(day) else "—"
    ev=pl[pl.date==dt].description.dropna().head(1).tolist()
    return cause, (ev[0][:48] if ev else "")
abn=[]
for _,r in top_ab.iterrows():
    c,e=context(r.date)
    abn.append({"date":str(r.date.date()),"z":float(r.z),"impact":int(r.impact),
                "cause":c,"event":e})

# ----------------------------------------------------------------------------- #
# EXPORT (extend dashboard feed)
# ----------------------------------------------------------------------------- #
dd["network"]={
  "nodes": nodes.assign(lat=nodes.lat.round(5),lon=nodes.lon.round(5),
            load=(nodes.load/1000).round(0)).to_dict("records"),
  "blast": {k:v for k,v in blast.items()},
  "diversion": {k:v for k,v in diversion.items() if v},
  "top_edges": edges[:12],
}
dd["coverage_curve"]={"busiest_dow":["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][busiest],
  "curve":curve,"u_for_50":units_for(50),"u_for_70":units_for(70),"u_for_80":units_for(80),
  "dispersed_units":dispersed[:8]}
dd["abnormal_days"]=abn
json.dump(dd,open(OUT/"dashboard_data.json","w"),indent=1,default=str)

print("NETWORK nodes:",len(nodes)," spillover edges (lift>1.1, c>=3):",len(edges))
print("\nTop spillover (A -> B, lift = times-above-chance):")
for e in edges[:8]: print(f"  {e['src']:<16} -> {e['dst']:<16}  x{e['lift']:<5} (n={e['count']})")
print("\nExample blast radius + diversion:")
for a in ["Mysore Road","ORR North 1","Bellary Road 1"]:
    b=", ".join(f"{x['corridor']}(x{x['lift']})" for x in blast.get(a,[])) or "—"
    dv=", ".join(f"{x['corridor']}({x['km']}km)" for x in diversion.get(a,[])) or "—"
    print(f"  {a}\n     spills to : {b}\n     divert via: {dv}")
print(f"\nCOVERAGE CURVE ({dd['coverage_curve']['busiest_dow']}):",curve)
print(f"  units for 50/70/80% = {units_for(50)}/{units_for(70)}/{units_for(80)}")
print("\nABNORMAL DAYS (z vs same-weekday baseline):")
for a in abn: print(f"  {a['date']}  z={a['z']:<5} impact={a['impact']:<7} {a['cause']:<16} {a['event']}")
print("\nExtended dashboard_data.json")
