import json, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("SAARTHI_OUT", str(ROOT / "outputs")))
d = json.load(open(OUT / "dashboard_data.json"))
DATA = json.dumps(d, default=str)

html = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SAARTHI — Bengaluru Traffic Ops Console</title>
<link rel="stylesheet" href="assets/vendor/leaflet.css"/>
<script src="assets/vendor/leaflet.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
:root{--ink:#0a111e;--panel:#111b2c;--panel2:#0d1626;--line:#22324a;--text:#e9eef6;
 --muted:#8294ae;--dim:#5a6c87;--saffron:#f5a524;--saffron2:#ffb84d;--teal:#2dd4bf;
 --red:#ff5d5d;--divert:#34d399;--barr:#ffd166;--amber:#ffb84d;}
*{box-sizing:border-box;margin:0;padding:0}html,body{height:100%}
body{background:var(--ink);color:var(--text);font-family:Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased;overflow:hidden}
.mono{font-family:'IBM Plex Mono',ui-monospace,'Courier New',monospace}
.app{display:grid;grid-template-columns:1fr 352px;grid-template-rows:60px 1fr;height:100vh}
header{grid-column:1/3;display:flex;align-items:center;gap:20px;padding:0 20px;z-index:700;
 background:linear-gradient(90deg,var(--panel2),var(--ink));border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:baseline;gap:12px}
.logo{font-family:Archivo,'Arial Black',sans-serif;font-weight:900;font-size:25px;letter-spacing:-.5px}.logo b{color:var(--saffron)}
.tag{font-size:11px;color:var(--muted);letter-spacing:.13em;text-transform:uppercase}
.kpis{display:flex;gap:10px;margin-left:auto}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:7px 14px;min-width:112px}
.kpi .v{font-family:Archivo;font-weight:800;font-size:19px;line-height:1.1}
.kpi .v.amber{color:var(--saffron)}.kpi .v.teal{color:var(--teal)}
.kpi .l{font-size:9px;color:var(--dim);text-transform:uppercase;letter-spacing:.09em;margin-top:2px}
#map{grid-column:1;grid-row:2;position:relative;background:#0a111e}
.leaflet-container{background:#0a111e;font-family:Inter}
.leaflet-popup-content-wrapper{background:var(--panel);color:var(--text);border:1px solid var(--line);border-radius:10px}
.leaflet-popup-tip{background:var(--panel)}
.pop b{color:var(--saffron2);font-family:Archivo}.pop .mono{color:var(--muted);font-size:11px}
.mapctl{position:absolute;z-index:600;left:14px;top:14px;background:rgba(13,22,38,.94);
 border:1px solid var(--line);border-radius:12px;padding:12px 14px;backdrop-filter:blur(6px);width:296px}
.mapctl h3{font-family:Archivo;font-size:11.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);margin-bottom:9px}
.dows{display:flex;gap:4px;margin-bottom:10px}
.dow{flex:1;text-align:center;padding:7px 0;font-size:11px;font-weight:600;border-radius:7px;background:var(--panel);border:1px solid var(--line);color:var(--muted);cursor:pointer;transition:.15s;font-family:'IBM Plex Mono'}
.dow:hover{border-color:var(--saffron)}.dow.on{background:var(--saffron);color:#1a1205;border-color:var(--saffron)}
.cov{display:flex;align-items:baseline;gap:8px}
.cov .big{font-family:Archivo;font-weight:900;font-size:33px;color:var(--teal);line-height:1}
.cov .lab{font-size:11px;color:var(--muted);line-height:1.3}
.scn{margin-top:10px;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:8px 10px}
.scn .ct{font-size:10px;color:var(--dim);text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px}
.scn select{width:100%;background:var(--panel2);color:var(--text);border:1px solid var(--line);border-radius:6px;
 padding:6px 8px;font-family:Inter;font-size:12px;cursor:pointer}
.scn .out{font-size:11px;color:var(--saffron2);margin-top:7px;line-height:1.4;min-height:14px}
.scn .out b{color:var(--teal)}
.krow{display:flex;align-items:center;gap:9px;margin-top:9px}
.krow label{font-size:10px;color:var(--dim);text-transform:uppercase;letter-spacing:.07em;white-space:nowrap}
.krow input[type=range]{flex:1;accent-color:var(--teal);height:3px}
.kval{font-family:'IBM Plex Mono';font-weight:600;color:var(--teal);font-size:13px;min-width:18px;text-align:right}
.pinrow{display:flex;gap:6px;margin-top:9px;align-items:center}
.pinbtn{flex:1;font-size:11px;padding:6px;text-align:center;border:1px solid var(--line);border-radius:6px;cursor:pointer;color:var(--muted);background:var(--panel2);transition:.15s}
.pinbtn.on{color:#1a1205;background:var(--saffron);border-color:var(--saffron)}
.pinrow input[type=number]{width:74px;background:var(--panel2);color:var(--text);border:1px solid var(--line);border-radius:6px;padding:5px 6px;font-family:'IBM Plex Mono';font-size:11px}
.pinclr{font-size:11px;padding:6px 9px;border:1px solid var(--line);border-radius:6px;cursor:pointer;color:var(--muted);background:var(--panel2)}
.curve{margin-top:10px;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:8px 10px}
.curve .ct{font-size:10px;color:var(--dim);text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px}
.curve .marks{display:flex;justify-content:space-between;font-size:10px;color:var(--muted);margin-top:4px;font-family:'IBM Plex Mono'}
.curve .marks b{color:var(--saffron2)}
.toggles{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap}
.tg{flex:1;min-width:58px;font-size:10px;padding:5px;text-align:center;border:1px solid var(--line);border-radius:6px;cursor:pointer;color:var(--muted);background:var(--panel)}
.tg.on{color:var(--text);border-color:var(--saffron2);background:rgba(245,165,36,.12)}
.legend{margin-top:10px;display:flex;align-items:center;gap:7px;font-size:10px;color:var(--dim)}
.ramp{height:7px;flex:1;border-radius:4px;background:linear-gradient(90deg,#1f4d8f,#22d3ee,#f5a524,#ff5d5d)}
.hint{font-size:10px;color:var(--dim);margin-top:9px;line-height:1.4;border-top:1px solid var(--line);padding-top:8px}
.hint b{color:var(--saffron2)}
aside{grid-column:2;grid-row:2;background:var(--panel2);border-left:1px solid var(--line);overflow-y:auto;padding:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:13px;margin-bottom:12px}
.card h2{font-family:Archivo;font-size:12px;letter-spacing:.07em;text-transform:uppercase;margin-bottom:3px;display:flex;align-items:center;gap:7px}
.card .sub{font-size:10.5px;color:var(--dim);margin-bottom:10px;line-height:1.45}
.dot{width:7px;height:7px;border-radius:50%;background:var(--saffron);flex:none}
.tagy{margin-left:auto;font-size:8.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--teal);border:1px solid rgba(45,212,191,.4);border-radius:5px;padding:2px 6px}
.row{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid rgba(34,50,74,.5);font-size:12px}
.row:last-child{border:0}
.row .name{color:var(--text);display:flex;align-items:center;gap:7px}.row .name small{color:var(--dim);display:block;font-size:10px}
.pill{font-family:'IBM Plex Mono';font-size:11px;font-weight:600}
.pill.t{color:var(--teal)}.pill.a{color:var(--saffron2)}.pill.r{color:var(--red)}.pill.b{color:var(--barr)}
.casc{font-size:11px;color:var(--muted);background:var(--panel2);border:1px solid var(--line);border-radius:7px;padding:7px 9px;margin-bottom:9px;line-height:1.4}
.casc b{color:var(--red)}.casc .x{color:var(--saffron2);font-family:'IBM Plex Mono'}
.ab{display:flex;gap:9px;align-items:center;padding:7px 0;border-bottom:1px solid rgba(34,50,74,.5)}
.ab:last-child{border:0}
.ztag{font-family:Archivo;font-weight:800;font-size:13px;color:var(--saffron2);min-width:40px}
.ab .meta{font-size:11px}.ab .meta b{color:var(--text)}.ab .meta small{color:var(--dim);display:block}
.lc .lr{display:flex;justify-content:space-between;font-size:10px;color:var(--muted);margin-top:5px;font-family:'IBM Plex Mono'}
.tdot{width:8px;height:8px;border-radius:2px;flex:none}
.tlegend{display:flex;gap:10px;font-size:9.5px;color:var(--muted);margin-bottom:9px;flex-wrap:wrap}
.tlegend span{display:flex;align-items:center;gap:4px}
.trap{background:linear-gradient(135deg,rgba(245,165,36,.1),rgba(45,212,191,.06));border:1px solid rgba(245,165,36,.3)}
.trap .tt{font-size:11.5px;color:var(--saffron2);font-weight:600;margin-top:8px}.trap p{font-size:11px;color:var(--muted);line-height:1.5;margin-top:2px}
.foot{font-size:10px;color:var(--dim);text-align:center;padding:6px}
@media(max-width:900px){.app{grid-template-columns:1fr}aside{display:none}.kpis{display:none}}
</style></head>
<body>
<div class="app">
 <header>
  <div class="brand"><div class="logo">SA<b>AR</b>THI</div>
   <div class="tag">Astram&nbsp;·&nbsp;Event-Driven Congestion Console</div></div>
  <div class="kpis">
   <div class="kpi"><div class="v" id="k_inc">—</div><div class="l">Incidents analysed</div></div>
   <div class="kpi"><div class="v amber" id="k_cm">—</div><div class="l">Congestion-min mapped</div></div>
   <div class="kpi"><div class="v teal" id="k_cap">—</div><div class="l">Risk capture @top20%</div></div>
   <div class="kpi"><div class="v teal" id="k_prev">—</div><div class="l">Congestion preventable</div></div>
  </div>
 </header>

 <div id="map">
  <div id="offline" style="display:none;position:absolute;z-index:650;right:14px;top:14px;background:rgba(255,93,93,.15);border:1px solid var(--red);color:#ffd0d0;font-size:11px;padding:7px 11px;border-radius:9px;backdrop-filter:blur(4px)">Offline — base map hidden, data layers active</div>
  <div class="mapctl">
   <h3>Deployment plan · by day</h3>
   <div class="dows" id="dows"></div>
   <div class="cov"><div class="big" id="covv">—</div>
    <div class="lab">of expected congestion-minutes<br>covered by <b><span id="kLabel">8</span> patrol anchors</b></div></div>
   <div class="scn">
    <div class="ct">What-if — re-optimise live</div>
    <select id="scnSel"><option value="-1">No added event (base plan)</option></select>
    <div class="krow"><label>Units (K)</label><input type="range" id="kSlider" min="2" max="16" step="1" value="8"><span class="kval" id="kVal">8</span></div>
    <div class="pinrow"><div class="pinbtn" id="pinBtn">📍 Drop custom event</div>
     <input type="number" id="pinImpact" value="600" min="50" step="50" title="impact (congestion-min)"></div>
    <div class="out" id="scnOut"></div>
   </div>
   <div class="curve">
    <div class="ct">Marginal coverage — how many units?</div>
    <svg id="curveSvg" width="266" height="46"></svg>
    <div class="marks"><span><b id="u50">–</b> → 50%</span><span><b id="u70">–</b> → 70%</span><span><b id="u80">–</b> → 80%</span></div>
   </div>
   <div class="toggles">
    <div class="tg on" id="tHeat">Risk heat</div><div class="tg on" id="tUnit">Units</div>
    <div class="tg on" id="tHot">Hotspots</div><div class="tg" id="tBarr">Barricades</div>
    <div class="tg" id="tNet">Spillover</div>
    <div class="tg" id="tBlind">Blind spots</div>
   </div>
   <div class="legend"><span>low</span><div class="ramp"></div><span>high</span></div>
   <div class="hint">Pick an event above to re-optimise the deployment live. Or open
    <b>Spillover</b> and click a corridor for its cascade + diversion.</div>
  </div>
 </div>

 <aside>
  <div class="card" style="background:linear-gradient(135deg,rgba(45,212,191,.1),rgba(245,165,36,.05));border:1px solid rgba(45,212,191,.35)">
   <h2><span class="dot" style="background:var(--teal)"></span>Would it have helped?<span class="tagy">counterfactual</span></h2>
   <div class="sub">We don't just predict — we back-test the plan against history. If SAARTHI's units had been pre-positioned, how much congestion was preventable?</div>
   <div id="cfact"></div>
   <div class="sub" style="margin:10px 0 5px">Reach equity — central zones hog coverage; periphery is starved. We surface it, not hide it.</div>
   <div id="equity"></div>
   <div id="auditNote" class="sub" style="margin-top:9px;color:var(--muted)"></div>
  </div>
  <div class="card">
   <h2><span class="dot" style="background:var(--barr)"></span>Barricading plan<span class="tagy">PS ask ✓</span></h2>
   <div class="sub">Where to physically place barricades for closures — real approaches + junctions, with the diversion to turn traffic onto. Dot = response urgency.</div>
   <div id="barr"></div>
  </div>
  <div class="card">
   <h2><span class="dot" style="background:var(--red)"></span>Spillover &amp; diversion<span class="tagy">PS ask ✓</span></h2>
   <div class="sub">Mined cascades within 90 min. Click a row to trace it on the map.</div>
   <div class="casc" id="casc">Click a corridor to see total system impact (direct + cascaded).</div>
   <div id="net"></div>
  </div>
  <div class="card">
   <h2><span class="dot" style="background:var(--saffron2)"></span>Emerging-event alarm</h2>
   <div class="sub">Spatio-temporal bursts (≥4 incidents, 1.5 km, 90 min) — sudden gatherings &amp; weather. Caught the Mar-7 city-wide rain flooding live.</div>
   <div id="gath"></div>
  </div>
  <div class="card">
   <h2><span class="dot" style="background:var(--teal)"></span>Post-event learning<span class="tagy">PS gap ✓</span></h2>
   <div class="sub">Walk-forward: re-fits each week on past data only, scored on the next unseen week. Capture holds &amp; rises — the nightly loop, proven.</div>
   <div class="lc"><svg id="learnSvg" width="318" height="56"></svg>
    <div class="lr"><span>wk1 · <b id="lf">–</b></span><span id="lm">mean –</span><span>wk<b id="lwk">–</b> · <b id="ll">–</b></span></div></div>
  </div>
  <div class="card hold">
   <h2><span class="dot"></span>Clearance hold-time<span class="tagy">manpower ✓</span></h2>
   <div class="sub">P50 typical · P90 plan-for. Dot = response urgency tier.</div>
   <div class="tlegend">
    <span><i class="tdot" style="background:var(--red)"></i>≤15 min</span>
    <span><i class="tdot" style="background:var(--amber)"></i>≤1 hr</span>
    <span><i class="tdot" style="background:var(--muted)"></i>standard</span></div>
   <div id="hold"></div>
  </div>
  <div class="card">
   <h2><span class="dot" style="background:var(--teal)"></span>Planned-event playbook</h2>
   <div class="sub">Archetypes parsed from field reports · median congestion-min</div>
   <div id="planned"></div>
  </div>
  <div class="card trap">
   <h2>⚑ Two traps we defused</h2>
   <div class="tt">Time is corrupted</div>
   <p>Raw hour-of-day peaks at 2 AM — a timezone + batch artifact. We drop it; key on day-of-week. (Same instinct keeps batch entries out of the alarm above.)</p>
   <div class="tt">Clearance time is mostly fake</div>
   <p>Batch auto-closes pile into a synthetic 2–3 h band. We flag them as censored and learn only from real signal.</p>
  </div>
  <div class="foot mono">SAARTHI · validated on 30 unseen days · learning proven over 13 weeks</div>
 </aside>
</div>

<script>
const D=__DATA__;const DOWN=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
const fmt=n=>Math.round(n).toLocaleString('en-IN');
const TC={red:'#ff5d5d',amber:'#ffb84d',std:'#8294ae',green:'#34d399'};
document.getElementById('k_inc').textContent=fmt(D.meta.incidents);
document.getElementById('k_cm').textContent=(D.meta.total_congestion_minutes/1e6).toFixed(2)+'M';
document.getElementById('k_cap').textContent=D.risk_metrics.capture_top20pct_model+'%';
document.getElementById('k_prev').textContent=D.counterfactual.prevented_pct+'%';

const map=L.map('map',{zoomControl:false,attributionControl:false}).setView([12.97,77.62],11);
L.control.zoom({position:'bottomright'}).addTo(map);
const tiles=L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{maxZoom:19});
let tileFail=0;tiles.on('tileerror',()=>{if(++tileFail===4){const n=document.getElementById('offline');if(n)n.style.display='block';}});
tiles.addTo(map);
function hav(la,lo,la2,lo2){const R=6371,p1=la*Math.PI/180,p2=la2*Math.PI/180,
 dp=(la2-la)*Math.PI/180,dl=(lo2-lo)*Math.PI/180,
 x=Math.sin(dp/2)**2+Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)**2;return 2*R*Math.asin(Math.sqrt(x));}

const heatMax=Math.max(...D.heat.map(h=>h.exp_impact));
function heatColor(v){const t=Math.min(1,v/heatMax);
 const s=[[31,77,143],[34,211,238],[245,165,36],[255,93,93]];
 const i=Math.min(2,Math.floor(t*3)),f=t*3-i,a=s[i],b=s[i+1];
 return`rgb(${a[0]+(b[0]-a[0])*f|0},${a[1]+(b[1]-a[1])*f|0},${a[2]+(b[2]-a[2])*f|0})`;}
let heatLayer=L.layerGroup(),hotLayer=L.layerGroup(),unitLayer=L.layerGroup(),
    netLayer=L.layerGroup(),barrLayer=L.layerGroup(),evtLayer=L.layerGroup(),blindLayer=L.layerGroup();
D.heat.forEach(h=>{const t=Math.min(1,h.exp_impact/heatMax);
 L.circle([h.lat,h.lon],{radius:380+Math.sqrt(h.exp_impact)*30,color:heatColor(h.exp_impact),
  weight:0,fillColor:heatColor(h.exp_impact),fillOpacity:0.18+0.32*t}).addTo(heatLayer);});
D.hotspots.forEach((h,i)=>{L.circleMarker([h.lat,h.lon],{radius:6,color:'#fff',weight:1.3,
  fillColor:'#f5a524',fillOpacity:.95}).bindPopup(`<div class="pop"><b>#${i+1} ${h.corridor}</b><br>
  <span class="mono">${h.per_day} congestion-min/day · ${h.n} incidents</span><br>
  dominant: <b>${h.cause.replace(/_/g,' ')}</b></div>`).addTo(hotLayer);});
heatLayer.addTo(map);hotLayer.addTo(map);

D.barricading.forEach(b=>{const ic=L.divIcon({className:'',iconSize:[20,20],html:
  `<div style="width:18px;height:18px;background:#ffd166;border:2px solid #0a111e;transform:rotate(45deg);box-shadow:0 0 0 1px #ffd166"></div>`});
 L.marker([b.lat,b.lon],{icon:ic}).bindPopup(`<div class="pop"><b>Barricade · ${b.junction}</b><br>
  <span class="mono">${b.barricade_points} points on ${b.corridor}<br>triggers: ${b.causes}<br>divert via: ${b.divert_via}</span></div>`).addTo(barrLayer);});

// ---- greedy max-coverage (live, in browser) ----
function greedy(weights,cells,K,reach,minsep){
 const cov=new Array(cells.length).fill(false),chosen=[];
 for(let s=0;s<K;s++){let bg=-1,bi=-1,bm=null;
  for(let i=0;i<cells.length;i++){if(chosen.includes(i))continue;
   if(chosen.some(c=>hav(cells[i].lat,cells[i].lon,cells[c].lat,cells[c].lon)<minsep))continue;
   let g=0,mask=[];
   for(let j=0;j<cells.length;j++){if(!cov[j]&&hav(cells[i].lat,cells[i].lon,cells[j].lat,cells[j].lon)<=reach){mask.push(j);g+=weights[j];}}
   if(g>bg){bg=g;bi=i;bm=mask;}}
  if(bi<0)break;bm.forEach(j=>cov[j]=true);chosen.push(bi);}
 let tot=0,got=0;weights.forEach((w,j)=>{tot+=w;if(cov[j])got+=w;});
 return{units:chosen.map(i=>({lat:cells[i].lat,lon:cells[i].lon})),coverage:100*got/(tot||1)};}

let curDow=null, curScn=-1, curK=8, customEvent=null, pinMode=false;
function paintUnits(units,cov){
 unitLayer.clearLayers();
 units.forEach((u,i)=>{
  L.circle([u.lat,u.lon],{radius:2500,color:'#2dd4bf',weight:1,dashArray:'4 5',fillColor:'#2dd4bf',fillOpacity:.05}).addTo(unitLayer);
  const ic=L.divIcon({className:'',iconSize:[26,26],html:`<div style="width:26px;height:26px;border-radius:50%;
   background:#2dd4bf;color:#04201c;font-family:Archivo;font-weight:900;font-size:13px;display:flex;align-items:center;
   justify-content:center;border:2px solid #0a111e;box-shadow:0 0 0 1px #2dd4bf">${i+1}</div>`});
  L.marker([u.lat,u.lon],{icon:ic}).addTo(unitLayer);});
 if(document.getElementById('tUnit').classList.contains('on'))unitLayer.addTo(map);
 const el=document.getElementById('covv');let c=0;clearInterval(window._ci);
 window._ci=setInterval(()=>{c+=cov/18;if(c>=cov){c=cov;clearInterval(window._ci);}el.textContent=c.toFixed(1)+'%';},18);}

// active event = chosen archetype OR a custom dropped pin (custom wins)
function activeEvent(){
 if(customEvent) return customEvent;
 if(curScn>=0){const a=D.scenario.archetypes[curScn];return {lat:a.lat,lon:a.lon,bump:a.bump,name:a.name,hold:a.p90_hold};}
 return null;}

function render(){
 evtLayer.clearLayers();
 const cells=D.scenario.cells, w=cells.map(c=>c.w[curDow]);
 const ev=activeEvent();
 if(ev){
  // add the event's congestion-min bump to cells within 1.5 km; if none, to the nearest cell
  let hit=false;
  cells.forEach((c,j)=>{if(hav(c.lat,c.lon,ev.lat,ev.lon)<=1.5){w[j]+=ev.bump;hit=true;}});
  if(!hit){let bi=0,bd=1e9;cells.forEach((c,j)=>{const dd=hav(c.lat,c.lon,ev.lat,ev.lon);if(dd<bd){bd=dd;bi=j;}});w[bi]+=ev.bump;}
 }
 // everything runs through the SAME live optimizer — base, K-slider, archetype, pin
 const r=greedy(w,cells,curK,D.scenario.reach_km,D.scenario.minsep_km);
 paintUnits(r.units,r.coverage);
 if(ev){
  const isPin=!!customEvent;
  const star=L.divIcon({className:'',iconSize:[30,30],html:`<div style="font-size:24px;line-height:30px;text-align:center;
   filter:drop-shadow(0 0 3px #000)">${isPin?'📍':'⭐'}</div>`});
  L.marker([ev.lat,ev.lon],{icon:star}).bindPopup(`<div class="pop"><b>${ev.name}</b><br>
   <span class="mono">+${fmt(ev.bump)} congestion-min${ev.hold?` · hold ≤${ev.hold} min`:''}</span></div>`).addTo(evtLayer);
  evtLayer.addTo(map);
  document.getElementById('scnOut').innerHTML=`<b>${ev.name}</b> on <b>${DOWN[curDow]}</b>
   (+${fmt(ev.bump)} cm)${ev.hold?` · hold ≤<b>${ev.hold}m</b>`:''} → ${curK} units re-optimised to <b>${r.coverage.toFixed(1)}%</b> coverage.`;
 } else {
  document.getElementById('scnOut').innerHTML=`<b>${curK} units</b> on <b>${DOWN[curDow]}</b> → <b>${r.coverage.toFixed(1)}%</b> coverage.`;
 }}

// coverage sparkline
(function(){const cv=D.coverage_curve,svg=document.getElementById('curveSvg'),W=266,H=46,P=4;
 const xs=cv.curve.map((_,i)=>P+i*(W-2*P)/(cv.curve.length-1)),ys=cv.curve.map(v=>H-P-(v/100)*(H-2*P));
 svg.innerHTML=`<path d="M${xs.map((x,i)=>x.toFixed(1)+','+ys[i].toFixed(1)).join(' L')}" fill="none" stroke="#2dd4bf" stroke-width="2"/>`+
  xs.map((x,i)=>`<circle cx="${x.toFixed(1)}" cy="${ys[i].toFixed(1)}" r="2" fill="${[cv.u_for_50-1,cv.u_for_70-1,cv.u_for_80-1].includes(i)?'#f5a524':'#2dd4bf'}"/>`).join('');
 document.getElementById('u50').textContent=cv.u_for_50;document.getElementById('u70').textContent=cv.u_for_70;document.getElementById('u80').textContent=cv.u_for_80;})();
// learning curve
(function(){const L2=D.learning_curve,svg=document.getElementById('learnSvg'),W=318,H=56,P=5;
 const v=L2.map(p=>p.capture),mn=Math.min(...v)-3,mx=Math.max(...v)+3;
 const xs=L2.map((_,i)=>P+i*(W-2*P)/(L2.length-1)),ys=v.map(x=>H-P-((x-mn)/(mx-mn))*(H-2*P));
 const ar=`M${xs[0]},${H-P} L`+xs.map((x,i)=>x.toFixed(1)+','+ys[i].toFixed(1)).join(' L')+` L${xs[xs.length-1]},${H-P} Z`;
 svg.innerHTML=`<path d="${ar}" fill="rgba(45,212,191,.12)"/><path d="M${xs.map((x,i)=>x.toFixed(1)+','+ys[i].toFixed(1)).join(' L')}" fill="none" stroke="#2dd4bf" stroke-width="2"/>`+
  xs.map((x,i)=>`<circle cx="${x.toFixed(1)}" cy="${ys[i].toFixed(1)}" r="2.2" fill="#2dd4bf"/>`).join('');
 document.getElementById('lf').textContent=v[0]+'%';document.getElementById('ll').textContent=v[v.length-1]+'%';
 document.getElementById('lwk').textContent=L2.length;document.getElementById('lm').textContent='mean '+(v.reduce((a,b)=>a+b,0)/v.length).toFixed(1)+'%';})();

// spillover net + cascade readout
const nodeByName={};D.network.nodes.forEach(n=>nodeByName[n.corridor]=n);
function showCascade(name){const c=D.cascade[name];const el=document.getElementById('casc');
 if(!c){el.textContent='';return;}
 el.innerHTML=`<b>${name}</b>: ${c.direct}k direct + ${c.cascaded}k cascaded =
  <b style="color:var(--saffron2)">${c.total}k</b> total system impact <span class="x">×${c.amplify}</span>`;}
function drawArcs(name){netLayer.clearLayers();const src=nodeByName[name];if(!src)return;showCascade(name);
 D.network.nodes.forEach(n=>{const sel=n.corridor===name;
  L.circleMarker([n.lat,n.lon],{radius:sel?8:5,color:sel?'#fff':'#7c8db0',weight:sel?2:1,
   fillColor:sel?'#f5a524':'#3a4a64',fillOpacity:.9}).addTo(netLayer)
   .on('click',()=>drawArcs(n.corridor)).bindTooltip(n.corridor,{direction:'top'});});
 (D.network.blast[name]||[]).forEach(b=>{const dst=nodeByName[b.corridor];if(!dst)return;
  L.polyline([[src.lat,src.lon],[dst.lat,dst.lon]],{color:'#ff5d5d',weight:1+Math.min(4,b.lift/6),opacity:.85}).addTo(netLayer);
  L.circleMarker([dst.lat,dst.lon],{radius:6,color:'#ff5d5d',weight:1.5,fillColor:'#ff5d5d',fillOpacity:.5})
   .bindTooltip(`spills here ×${b.lift}`,{direction:'top'}).addTo(netLayer);});
 (D.network.diversion[name]||[]).forEach(dv=>{const dst=nodeByName[dv.corridor];if(!dst)return;
  L.polyline([[src.lat,src.lon],[dst.lat,dst.lon]],{color:'#34d399',weight:2,opacity:.85,dashArray:'5 5'}).addTo(netLayer);
  L.circleMarker([dst.lat,dst.lon],{radius:6,color:'#34d399',weight:1.5,fillColor:'#34d399',fillOpacity:.5})
   .bindTooltip(`divert via (${dv.km} km)`,{direction:'top'}).addTo(netLayer);});
 if(document.getElementById('tNet').classList.contains('on'))netLayer.addTo(map);}

// dow buttons
const dowsEl=document.getElementById('dows');
curDow=+Object.entries(D.dow_load).sort((a,b)=>b[1]-a[1])[0][0];
DOWN.forEach((d,i)=>{const b=document.createElement('div');b.className='dow'+(i===curDow?' on':'');
 b.textContent=d;b.onclick=()=>{document.querySelectorAll('.dow').forEach(x=>x.classList.remove('on'));
 b.classList.add('on');curDow=i;render();};dowsEl.appendChild(b);});
// scenario select
const sel=document.getElementById('scnSel');
D.scenario.archetypes.forEach((a,i)=>{const o=document.createElement('option');o.value=i;
 o.textContent=`${a.name}  (+${fmt(a.bump)} cm)`;sel.appendChild(o);});
sel.onchange=()=>{curScn=+sel.value;customEvent=null;setPin(false);render();};

// K slider — live re-optimise with a different number of patrol units
const kS=document.getElementById('kSlider'),kV=document.getElementById('kVal'),kL=document.getElementById('kLabel');
kS.oninput=()=>{curK=+kS.value;kV.textContent=curK;if(kL)kL.textContent=curK;render();};

// pin-drop — drop a custom event anywhere and re-optimise around it
function setPin(on){pinMode=on;const b=document.getElementById('pinBtn');
 b.classList.toggle('on',on);b.textContent=on?'📍 Click the map…':'📍 Drop custom event';
 map.getContainer().style.cursor=on?'crosshair':'';}
document.getElementById('pinBtn').onclick=()=>setPin(!pinMode);
map.on('click',e=>{if(!pinMode)return;
 const bump=Math.max(50,+document.getElementById('pinImpact').value||600);
 customEvent={lat:e.latlng.lat,lon:e.latlng.lng,bump,name:'Custom event',hold:null};
 sel.value='-1';curScn=-1;setPin(false);render();
 map.panTo([e.latlng.lat,e.latlng.lng]);});

render();

function tog(id,layer,onAdd){const el=document.getElementById(id);el.onclick=()=>{el.classList.toggle('on');
 if(el.classList.contains('on')){layer.addTo(map);onAdd&&onAdd();}else map.removeLayer(layer);};}
tog('tHeat',heatLayer);tog('tHot',hotLayer);tog('tUnit',unitLayer);tog('tBarr',barrLayer);
tog('tNet',netLayer,()=>{if(netLayer.getLayers().length===0)drawArcs('Hosur Road');});
tog('tBlind',blindLayer);

// rails
const tierOf=c=>D.urgency.tier[c]||'std';
// ---- proven-impact card: counterfactual + equity + confidence ----
(function(){
 const c=D.counterfactual;
 document.getElementById('cfact').innerHTML=
  `<div style="display:flex;align-items:baseline;gap:8px;margin-bottom:4px">
    <span style="font-family:Archivo;font-weight:900;font-size:30px;color:var(--teal);line-height:1">${c.prevented_pct}%</span>
    <span style="font-size:11px;color:var(--muted);line-height:1.3">of congestion-minutes preventable<br>(${fmt(c.prevented_congestion_min)} min) by pre-positioning</span></div>
   <div class="row"><div class="name">Incidents reached (≤${c.reach_km} km)</div><span class="pill t">${c.reach_pct}%</span></div>
   <div class="row"><div class="name">High-impact incidents reached</div><span class="pill t">${c.esc_reach_pct}%</span></div>`;
 const eq=D.equity, mx=Math.max(...eq.zones.map(z=>z.reached_pct));
 const eEl=document.getElementById('equity');
 eq.zones.slice(0,3).concat(eq.zones.slice(-1)).forEach(z=>{const r=document.createElement('div');r.className='row';
  const col=z.reached_pct<20?'var(--red)':z.reached_pct<50?'var(--amber)':'var(--teal)';
  r.innerHTML=`<div class="name" style="flex:1">${z.zone}
   <div class="bar"><i style="width:${100*z.reached_pct/mx}%;background:${col}"></i></div></div>
   <span class="pill" style="color:${col};margin-left:8px">${z.reached_pct}%</span>`;eEl.appendChild(r);});
 const small=document.createElement('div');small.className='sub';small.style.marginTop='7px';
 small.innerHTML=`Reach gap <b style="color:var(--red)">${eq.gap_pct} pts</b> between best & worst zone. ${eq.note}`;
 eEl.appendChild(small);
 const a=D.confidence_audit;
 document.getElementById('auditNote').innerHTML=
  `<b style="color:var(--saffron2)">Self-audit:</b> median forecast confidence ${a.median_confidence}/100;
   ${a.low_confidence_cells.length} low-confidence zones flagged on the map (toggle “Blind spots”). ${a.note}`;
 // low-confidence map layer
 a.low_confidence_cells.forEach(cc=>{L.circleMarker([cc.lat,cc.lon],{radius:9,color:'#ff5d5d',weight:1.5,
   dashArray:'3 3',fill:false}).bindTooltip(`low confidence (${cc.confidence}/100, ${cc.incidents} incidents)`,
   {direction:'top'}).addTo(blindLayer);});
})();

const barrEl=document.getElementById('barr');
D.barricading.slice(0,5).forEach(b=>{const tcause=b.causes.split(',')[0].trim();const r=document.createElement('div');
 r.className='row';r.style.cursor='pointer';r.onclick=()=>{document.getElementById('tBarr').classList.add('on');
  barrLayer.addTo(map);map.setView([b.lat,b.lon],14);};
 r.innerHTML=`<div class="name"><i class="tdot" style="background:${TC[tierOf(tcause)]}"></i>
  <span>${b.junction!=='(approach)'?b.junction:b.corridor}<small>${b.corridor} · ${b.causes}</small></span></div>
  <span class="pill b">${b.barricade_points}×</span>`;barrEl.appendChild(r);});

const netEl=document.getElementById('net');
D.network.top_edges.slice(0,5).forEach(e=>{const r=document.createElement('div');r.className='row';r.style.cursor='pointer';
 r.onclick=()=>{document.getElementById('tNet').classList.add('on');netLayer.addTo(map);drawArcs(e.src);
  map.setView([nodeByName[e.src].lat,nodeByName[e.src].lon],12);};
 r.innerHTML=`<div class="name">${e.src} → ${e.dst}<small>${e.count} cascades observed</small></div>
  <span class="pill r">×${e.lift}</span>`;netEl.appendChild(r);});

const gathEl=document.getElementById('gath');
D.gatherings.slice(0,5).forEach(g=>{const el=document.createElement('div');el.className='ab';
 el.innerHTML=`<div class="ztag">${g.size}×</div><div class="meta"><b>${g.date} · ${g.area}</b>
  <small>${g.cause.replace(/_/g,' ')}${g.desc?' — '+g.desc.replace(/\n/g,' '):''}</small></div>`;gathEl.appendChild(el);});

const holdEl=document.getElementById('hold');
D.clearance_by_cause.slice(0,7).forEach(c=>{const r=document.createElement('div');r.className='row';
 r.innerHTML=`<div class="name"><i class="tdot" style="background:${TC[tierOf(c.cause)]}"></i>
  <span>${c.cause.replace(/_/g,' ')}<small>${D.urgency.label[tierOf(c.cause)]}</small></span></div>
  <div style="text-align:right"><span class="pill a">${c.P50_min}m</span> / <span class="pill r">${c.P90_min}m</span></div>`;holdEl.appendChild(r);});

const plEl=document.getElementById('planned');
D.planned_archetypes.filter(p=>p.arch!=='Other planned').sort((a,b)=>b.med_impact-a.med_impact)
 .forEach(p=>{const r=document.createElement('div');r.className='row';
  r.innerHTML=`<div class="name">${p.arch}<small>${p.events} events · ${p.closures} closures</small></div>
   <span class="pill a">${fmt(p.med_impact)}</span>`;plEl.appendChild(r);});
</script>
</body></html>"""
open(ROOT / "index.html","w").write(html.replace("__DATA__",DATA))
print("rebuilt",len(html),"bytes")
