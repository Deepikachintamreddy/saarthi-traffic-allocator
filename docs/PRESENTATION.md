# 🎯 SAARTHI Presentation Slide Deck Outline

This outline is designed for a **7-8 Slide Pitch Deck** (approx. 5-7 minutes presentation). It focuses on presenting your project with maximum professional credibility, business alignment, and technical depth.

---

## Slide 1: Cover & The Hook
* **Title**: SAARTHI — Spatio-temporal Allocation, Anomaly & Risk Triage for High-impact Incidents
* **Subtitle**: Event-Driven Traffic Prediction & Resource Optimization Console for BTP
* **Visuals**: A high-resolution desktop screenshot of the SAARTHI Console showing the dark-theme Leaflet map, heatmap, and teal patrol markers.
* **Key Content**:
  * Hackathon Track: Theme 2 — Event-Driven Congestion (Planned & Unplanned)
  * Presenter Name(s)
* **Speaker Notes (15s)**:
  > *"Good morning judges. Today, Bengaluru's traffic police deploy enforcement units primarily based on gut feel and static historical beats. We built SAARTHI—an end-to-end predictive and prescriptive console that forecasts event-driven traffic impact, mathematically optimizes patrol locations, recommends barricading/diversions, and updates itself nightly via a closed learning loop."*

---

## Slide 2: The Core Problem & Hidden Data Traps
* **Title**: Why Event-Driven Congestion is Hard: The Hidden Dataset Traps
* **Visuals**: Two side-by-side charts/callouts:
  1. A bar chart showing the 2 AM raw reporting spike (Trap A).
  2. A distribution plot showing the 120–180 minute auto-close spike (Trap B).
* **Key Content**:
  * **The Jitter Trap (Time)**: Raw start hours peak at 2 AM IST (timezone tags and batch creation artifacts, not rush hour). We drop absolute hours and map risk to Day-of-Week + coarse Day-Part bins.
  * **The Fake Duration Trap (Clearance)**: ~46% of raw clearance times are batch auto-closes (synthetic 2–3 hour band). We flag these as right-censored and train only on human-resolved clearance signals.
* **Speaker Notes (45s)**:
  > *"Before training any models, we realized this dataset had two hidden traps that would sink a naive approach. First, the reporting time is corrupted—showing a massive peak at 2 AM due to timezone batch uploads. Second, nearly half of the clearance times are fake auto-closes. We defused both traps: we dropped raw hours to prevent learning temporal noise, and treated the auto-closes as right-censored data, ensuring our models train only on clean, trustworthy signal."*

---

## Slide 3: The Unified Metric — Congestion-Minutes
* **Title**: Moving From Event Counts to Expected Congestion-Minutes
* **Visuals**: A mathematical block diagram showing the formula:
  $$\text{Congestion-Minutes} = \text{Severity (Priority, Closure, Text)} \times \text{Corridor Criticality} \times \text{Expected Clearance Time}$$
  * A KPI card showing **2.55M cumulative congestion-minutes** mapped.
* **Key Content**:
  * **Event Severity**: Scored via multi-modal inputs (incident priority, road closure requests, and Kannada/English NLP text classifiers).
  * **Corridor Criticality**: Dynamic weighting based on historical shares of high-priority closures per corridor.
  * **Expected Clearance**: Predicted duration per incident.
* **Speaker Notes (30s)**:
  > *"Most teams will try to forecast how many events happen. We do something different: we calculate expected 'congestion-minutes'—a single physical currency representing severity, road closure impact, Kannada/English text reports, and expected clearance time. This lets us rank and optimize against actual city-wide delay, not just raw event frequencies."*

---

## Slide 4: The Predictive Engine
* **Title**: Spatio-Temporal Risk Surface & Clearance Models
* **Visuals**: 
  * A screenshot of the risk heatmap overlay in the console.
  * A table showing model performance lift.
* **Key Content**:
  * **Risk Forecaster (HistGBM)**: Fits a panel of 241 grid cells ($~1.3\text{ km}$ resolution) $\times$ DOW to predict expected daily congestion-minutes.
  * **Clearance Model**: Censoring-aware quantile regressors predicting P50 (typical) and P90 (worst-case plan-for) hold times.
  * **Validation (30 Unseen Days)**:
    * Risk capture rate: **67.8%** of next month's congestion captured in the top-20% highest-risk cells.
    * Clearance model error: **32.8% lower MAE** than standard average baselines.
* **Speaker Notes (45s)**:
  > *"Our predictive engine has two parts. A Gradient Boosting risk forecaster predicts the daily expected congestion-minute surface across 241 cells in Bengaluru. A second model estimates typical and worst-case clearance hold times. Validated on 30 completely unseen days, deploying patrols to our top 20% highest-risk cells captures 67.8% of all subsequent traffic delays, while our clearance model outperforms flat average baselines by 32.8%."*

---

## Slide 5: Prescriptive Optimization & Manpower Sizing
* **Title**: Pre-Positioning Optimizer & The Coverage Curve
* **Visuals**: 
  * The teal circular patrol boundary markers on the Leaflet map.
  * The **Marginal Coverage Curve** chart (from `index.html`'s SVG sparkline).
* **Key Content**:
  * **Greedy Max-Coverage**: Solves the location-allocation problem. Places $K$ patrol units to maximize covered expected congestion-minutes (under a 2.5 km reach and 1.8 km separation constraint).
  * **Force Sizing**: The marginal coverage curve shows exactly what percentage of city-wide delay is covered per unit added:
    $$\mathbf{6 \text{ units} \rightarrow 50\%} \quad\mid\quad \mathbf{10 \text{ units} \rightarrow 70\%} \quad\mid\quad \mathbf{14 \text{ units} \rightarrow 80\%}$$
  * **Barricading Plan**: Clusters road closure approaches into ranked junctions with recommended barricade counts.
* **Speaker Notes (45s)**:
  > *"For resource deployment, we solve a greedy location-allocation problem. The console places $K$ patrol anchors to cover maximum congestion-minutes. Instead of guessing force sizes, we present the Marginal Coverage Curve: 6 units cover 50% of Bengaluru's expected event congestion, 10 units hit 70%, and 14 hit 80%. This lets BTP size the deployment to a target coverage budget. For road closures, we also recommend exact physical barricade points at approaching junctions."*

---

## Slide 6: The Spillover Network & Diversions
* **Title**: Spillover Cascades & Blast-Radius Diversions
* **Visuals**: 
  * A screenshot of the red spillover arc (e.g., Hosur Road to Thanisandra) and the green parallel diversion route on the map.
  * A table listing top spillovers by lift (e.g., Hosur Road $\rightarrow$ IRR/Thanisandra at $28.5\times$ normal odds).
* **Key Content**:
  * **Temporal Spillover mining**: Mines transitions where an incident on corridor A triggers another within 90 minutes / 4 km.
  * **System Amplification Factor**: Shows Hosur Road generates 103k direct + 85k cascaded minutes ($1.82\times$ amplification).
  * **Blast-Radius Exclusions**: Recommends diversions onto nearest parallel corridors that are *outside* the primary cascade's path.
* **Speaker Notes (45s)**:
  > *"Here is our core differentiator: We don't treat roads in isolation. We mined the logs to build a directed spillover network. For example, if Hosur Road chokes, it triggers a cascade onto Thanisandra/IRR at 28 times normal odds, amplifying its impact to 1.8 times the direct delay. Our diversion system uses this network to recommend rerouting traffic onto parallel arterials that are explicitly outside the spillover blast radius, preventing cascading gridlocks."*

---

## Slide 7: Live Interaction, Scenarios & Continuous Learning
* **Title**: Real-time What-If Simulation & Nightly Learning Loops
* **Visuals**: 
  * A screenshot of the **What-if panel** showing the **K-slider** and the **📍 Pin-Drop** action.
  * The weekly learning curve graph showing capture rate stability over 13 weeks.
* **Key Content**:
  * **Live Client-Side Re-optimization**: Drag the $K$-slider or drop a custom event pin on the map, and the greedy optimizer re-runs live in the browser.
  * **Post-Event Learning**: Walk-forward weekly re-fitting. Captures **61.5% $\rightarrow$ 66.9%** (mean **64.8%**) over 13 weeks.
  * **Emerging-Event Alarm**: Real-time bursts ($\ge 4$ incidents in 1.5 km / 90 min) caught the March 7 city-wide flooding live.
* **Speaker Notes (45s)**:
  > *"SAARTHI is a live decision tool, not a static report. In the browser, a commander can drag the available units slider, or click 'Drop Custom Event' to pin an unannounced rally. The console re-runs the optimizer in JavaScript instantly. Finally, we implement a nightly walk-forward learning loop: the model re-fits weekly on past logs and predicts the next week, proving in code that the risk surface holds stable at ~65% capture as data accumulates."*

---

## Slide 8: Technology Stack & Operational Deployment
* **Title**: Lightweight, Self-Contained, and Deployable
* **Visuals**: A clean architectural icon strip (Python $\rightarrow$ Pandas $\rightarrow$ Scikit-Learn $\rightarrow$ JSON $\rightarrow$ Leaflet.js).
* **Key Content**:
  * **Backend**: Lightweight Python ETL and ML pipeline (HistGradientBoosting).
  * **Frontend**: Pure vanilla JS, CSS, and SVG map rendering (no framework overhead).
  * **Offline Resilience**: Leaflet library and assets are fully vendored locally. If cellular network connectivity fails in the field, the dashboard remains active and fully interactive.
  * **Vercel Hosted**: Ready to deploy with continuous integration on git push.
* **Speaker Notes (30s)**:
  > *"Our entire system is lightweight and production-ready. The ML and network mining backend are written in Python, exporting a single compressed data payload. The frontend is vanilla HTML/JS and Leaflet, completely offline-resilient—if network tiles fail in the field, the data layers keep rendering. We have hosted our final submission live on Vercel at saarthi-traffic-allocator.vercel.app. Thank you, and we are open to questions!"*
