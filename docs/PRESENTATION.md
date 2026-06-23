# 🎯 SAARTHI Presentation Slide Deck Outline (11 Slides)

This document contains a comprehensive, slide-by-slide outline for a **10+ Slide Pitch Deck** (specifically 11 slides) detailing the SAARTHI system. Each slide outline specifies the slide title, recommended visual layout, core bullet points with exact project metrics, and a verbatim speaker script.

---

## Slide 1: Cover & The Hook (Project Pitch)
*   **Slide Title**: SAARTHI — Spatio-temporal Allocation, Anomaly & Risk Triage for High-impact Incidents
*   **Subtitle**: Event-Driven Traffic Prediction & Resource Optimization Console for Bengaluru Traffic Police (BTP)
*   **Visual Layout**: Dark-themed slide. The left half displays the project title and hackathon metadata. The right half shows a full-screen desktop mockup of the SAARTHI Leaflet map running in dark mode with active heat layers and patrol anchors.
*   **Core Content**:
    *   **Theme**: Theme 2 — Event-Driven Congestion (Planned & Unplanned)
    *   **Core Delivery**: A lightweight, offline-resilient operations console that predicts, prioritizes, allocates, and learns.
    *   **Presenter Name**: Deepika Chintamreddy
*   **Speaker Script (15s)**:
    > *"Good evening, judges. Today, traffic police deployment in Bengaluru is largely experience-driven, and event impacts are not quantified in advance. We built SAARTHI—a complete decision console that predicts traffic risk, quantifies delay in expected congestion-minutes, optimizes patrol and barricading deployment mathematically, and refines itself nightly through an active learning loop."*

---

## Slide 2: Executive Summary (The Paradigm Shift)
*   **Slide Title**: The Core Paradigm Shift: Congestion-Minutes & Supply-Chain Optimization
*   **Visual Layout**: A simple, bold comparison layout. On the left: "Conventional Systems: Count Events" (red X). On the right: "SAARTHI: Forecast Expected Delay Currency" (green checkmark).
*   **Core Bullet Points**:
    *   **The Currency**: We do not predict incident frequency; we predict **congestion-minutes** (Severity $\times$ Criticality $\times$ Clearance Duration).
    *   **The Logistics Playbook**: Applies supply-chain fleet optimization to public safety—forecast demand $\rightarrow$ position patrol fleet $\rightarrow$ trigger feedback.
    *   **Actionable Outputs**: Automatically produces coordinates for patrol anchors, junction barricade points, and spillover-free diversions.
*   **Speaker Script (30s)**:
    > *"Most approaches try to forecast the raw count of traffic incidents. SAARTHI shifts this paradigm. We forecast expected 'congestion-minutes'—a single physical currency representing the total cumulative delay an incident will generate. By mapping this risk surface, we can apply supply-chain logistics principles to public safety: predicting traffic demand, pre-positioning the patrol fleet, and closing the loop with nightly updates."*

---

## Slide 3: Data Spine & Defusing Hidden Data Traps
*   **Slide Title**: Data Integrity: Defusing the Dataset Traps
*   **Visual Layout**: Split layout with warning alerts (`[!WARNING]`). 
    *   *Left Box*: Trap A (Time Corruption) with a bar chart showing the fake 2 AM IST spike.
    *   *Right Box*: Trap B (Duration Corruption) showing the fake 120–180 minute auto-close duration peak.
*   **Core Bullet Points**:
    *   **Trap A (Time Jitter)**: Stored incident start times spike artificially at 2 AM due to timezone/batch uploads. SAARTHI discards absolute hours and keys on Day-of-Week (DOW) and coarse Day-Part bins.
    *   **Trap B (Auto-Close Artifacts)**: $\sim 46\%$ of closed records pile into a synthetic 2–3 hour band due to auto-close scripts. We flag these as right-censored, training models only on trustworthy human-resolved signals.
*   **Speaker Script (45s)**:
    > *"A machine learning model is only as good as its data. We identified and defused two massive traps in the Astram log. First, the reporting time is corrupted—showing a fake peak at 2 AM due to timezone tagging and batch uploads. Second, nearly half of all clearance durations are auto-close artifacts. We resolved both: we collapsed absolute hours into Day-Parts to bypass timezone jitter, and treated the auto-close entries as right-censored data so they cannot skew our predictions."*

---

## Slide 4: Multi-Modal Impact Quantification (CIQ)
*   **Slide Title**: The CIQ Engine: Congestion-Impact Quantifier
*   **Visual Layout**: Centered equation layout:
    $$\text{Impact (Minutes)} = \text{Severity Factor} \times \text{Corridor Criticality} \times \text{Expected Clearance Duration}$$
    *   Below the equation, show three KPI callout cards: Severity, Criticality, and Expected Clearance.
*   **Core Bullet Points**:
    *   **Severity Factor**: Combines priority (High = 2.0x, Low = 1.0x), closure requests (1.8x), and text signal mined via bilingual NLP (-1 to +1 based on English/Kannada field reports).
    *   **Corridor Criticality**: Dynamic weighting ($1.0 \text{ to } 2.0$) measuring the historical share of severe/closure events on each corridor.
    *   **Expected Clearance**: Expected duration predicted per incident cause.
*   **Speaker Script (30s)**:
    > *"To calculate expected congestion-minutes, we developed the Congestion-Impact Quantifier, or CIQ. It fuses incident priority, closure requirements, and Kannada/English report text using bilingual NLP. It weights this severity by a corridor criticality index—which scales from 1 to 2 to prioritize arterial roads—and multiplies it by the incident's predicted clearance time."*

---

## Slide 5: Spatio-Temporal Risk Surface Forecasting
*   **Slide Title**: Mapping the City's Risk Surface
*   **Visual Layout**: Left: Risk surface heatmap displaying high-density hot zones in Bengaluru. Right: Validation metrics.
*   **Core Bullet Points**:
    *   **Grid Panel Model**: Aggregates the city into a spatial grid of 241 cells ($~1.3\text{ km}$ resolution) tracked across DOW and Day-Parts.
    *   **Risk Model**: Uses a `HistGradientBoostingRegressor` to predict expected daily congestion-minutes per cell.
    *   **Strict Time Validation**: Evaluated on 30 completely unseen days. The top 20% highest-risk cells capture **67.8%** of all actual next-month congestion-minutes (outperforming the cell-mean baseline of 66.1%).
*   **Speaker Script (45s)**:
    > *"Our predictive core models the city as a spatio-temporal panel. We segment Bengaluru into 241 cells and train a Histogram Gradient Boosting Regressor to predict the expected daily congestion-minutes for every cell. Validated on 30 completely unseen days, deploying to the top 20% of cells flagged by our model captures 67.8% of the next month's real congestion, outperforming static historical baselines."*

---

## Slide 6: Clearance Time Prediction (Quantile Models)
*   **Slide Title**: Quantile Models for Patrol Unit Commitment Time
*   **Visuals**: A horizontal bar chart showing P50 (typical) vs. P90 (worst-case) clearance hold times by cause (Protest: 142m / 396m; Public Event: 112m / 332m; Construction: 43m / 315m; Tree Fall: 20m / 296m).
*   **Core Bullet Points**:
    *   **Quantile Regressors**: Separate gradient boosters trained on Quantile Loss at $q=0.5$ (median typical) and $q=0.9$ (worst-case plan-for).
    *   **Commitment Sizing**: Tells dispatchers exactly how long a unit will be tied up at a scene (e.g., protest hold $\le$ 396m).
    *   **Accuracy Lift**: Achieves a **32.8% lower MAE** (Mean Absolute Error) compared to flat historical averages.
*   **Speaker Script (40s)**:
    > *"When an incident occurs, dispatchers need to know how long a patrol unit will be committed. Instead of a flat average, we train censoring-aware quantile regressors. This outputs a P50 typical hold time and a P90 worst-case planning time per cause. For example, a protest has a P50 of 142 minutes but a P90 of 396 minutes. This quantile modeling reduces prediction error by 32.8% over flat averages."*

---

## Slide 7: Prescriptive Patrol Pre-Positioning
*   **Slide Title**: Patrol Pre-Positioning: Mathematical Allocation
*   **Visual Layout**: Left: Leaflet map view showing optimized unit locations (teal dots 1–8) with their 2.5 km coverage radii. Right: Allocation rules.
*   **Core Bullet Points**:
    *   **Greedy Max-Coverage**: Solves the location-allocation problem. Selects $K$ coordinates that cover the maximum expected congestion-minutes.
    *   **Spatial Constraints**: Units are restricted to a maximum reach of 2.5 km and enforced with a minimum separation of 1.8 km to prevent redundant stacking.
    *   **Adaptive Scheduling**: Automatically generates different, optimized patrol coordinates for each day of the week based on changing risk patterns.
*   **Speaker Script (45s)**:
    > *"To allocate manpower, we solve a greedy max-coverage location-allocation problem. The model determines the optimal coordinates for $K$ patrol anchors to cover the maximum predicted risk. We enforce a 2.5 km operational reach and a 1.8 km separation constraint to ensure units are spread out. The console automatically generates different, day-specific coordinates for every day of the week."*

---

## Slide 8: Resource-Coverage Curves (Manpower Sizing)
*   **Slide Title**: The Marginal Resource-Coverage Curve
*   **Visual Layout**: A line chart mapping the number of patrol units ($X$-axis, 1 to 15) against the cumulative percentage of congestion-minutes covered ($Y$-axis, 0% to 100%).
*   **Core Bullet Points**:
    *   **Data-Driven Staffing**: Quantifies the marginal returns of adding more patrol vehicles.
    *   **Key Threshold Metrics**:
        *   **6 units** capture **50%** of expected daily congestion.
        *   **10 units** capture **70%** of expected daily congestion.
        *   **14 units** capture **80%** of expected daily congestion.
    *   **Command Tool**: Allows BTP to mathematically size the dispatch force to meet a specific coverage target.
*   **Speaker Script (40s)**:
    > *"BTP commanders often ask: 'How many units do we need?' We answer this with our Marginal Resource-Coverage Curve. The math shows distinct thresholds: 6 units capture 50% of the city's expected event-driven delay, 10 units cover 70%, and 14 units hit 80%. This curve removes guesswork, allowing BTP to size their deployment based on real statistical coverage targets."*

---

## Slide 9: Barricading & Safe-Radius Diversion Plans
*   **Slide Title**: Precision Barricading & Spillover-Free Diversions
*   **Visual Layout**: Screenshot of the "Barricading plan" card showing junctions, barricade counts, and recommended diversion routes next to the Leaflet map overlay.
*   **Core Bullet Points**:
    *   **Barricade Recommender**: Clusters road-closure segment approaches into persistent zones. Recommends exact locations (e.g., K R Circle, K R Market) and barricade counts (2–4 points).
    *   **Spillover-Free Diversion**: Finds the nearest parallel corridors (e.g., ORR West, Magadi Road) while mathematically filtering out roads inside the incident's cascade blast radius.
*   **Speaker Script (40s)**:
    > *"When road closures are required, SAARTHI automatically recommends precision barricading and diversion plans. It clusters segment approaches to recommend physical barricading points at named junctions. It then identifies parallel diversion corridors. Crucially, the system checks our cascade network to ensure recommended diversions direct traffic onto roads that are safe from spillover."*

---

## Slide 10: Corridor Spillover Cascade Network
*   **Slide Title**: Mined Corridor Spillovers & Cascading Impact
*   **Visual Layout**: A directed network graph showing corridors (nodes) and spillover probabilities (edges). Highlight Hosur Road pointing to IRR/Thanisandra.
*   **Core Bullet Points**:
    *   **Cascade Association Mining**: Identifies temporal-spatial propagation where an incident on corridor A triggers a cascade on corridor B within 90 minutes.
    *   **Top Edge Cascades**: Mapped strongest transition: **Hosur Road $\rightarrow$ IRR/Thanisandra at $28.5\times$ normal odds** (167 observed cascades).
    *   **System Amplification**: Measures direct vs. derived impact. E.g., Hosur Road: 103k direct + 85k cascaded = 188k total system impact ($1.82\times$ amplification).
*   **Speaker Script (45s)**:
    > *"Instead of viewing corridors in isolation, we mined the logs to build a directed spillover network. We track how gridlock propagates across Bengaluru's geometry. Our model reveals that a choke on Hosur Road triggers follow-on delays on Thanisandra at 28.5 times normal odds. By calculating these cascades, we show that Hosur Road's true systemic cost is 1.82 times its direct delay, highlighting the critical corridors that command immediate triage."*

---

## Slide 11: Alarms, Live What-If Simulator & Learning Loops
*   **Slide Title**: Live What-If Simulation & Nightly Learning Loops
*   **Visual Layout**: Left: UI screenshot of the browser-side What-If event select dropdown, the K-slider, and the custom event pin-drop. Right: Learning curve showing weekly capture rate over 13 weeks.
*   **Core Bullet Points**:
    *   **Live Browser Re-optimization**: Users can adjust the $K$-slider or drop a custom event pin anywhere on the Leaflet map; the greedy optimizer re-runs live in JS.
    *   **Spatio-Temporal Burst Alarm**: Detects unplanned gatherings ($\ge 4$ incidents in 1.5 km / 90 min) while filtering out batch survey logs.
    *   **Post-Event Learning Loop**: Simulates walk-forward weekly retraining. Average capture rate holds stable at **64.8%** over 13 weeks.
*   **Speaker Script (45s)**:
    > *"Finally, SAARTHI is a live tool. In our console, a commander can drag the available units slider or drop a custom pin on the map. The Leaflet map runs our greedy optimizer live in JavaScript to instantly update coordinates. To close the loop, we implement a walk-forward learning loop: the model re-fits weekly on past logs and predicts the next week, proving in code that our risk capture holds stable at 65% as data accumulates."*
