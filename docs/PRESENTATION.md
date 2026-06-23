# 🚦 SAARTHI Pitch Deck: 10-Slide Outline & Script

This document provides the structured slide-by-slide content, visual layouts, core technical bullet points, and verbatim speaker scripts for presenting **SAARTHI** at the Gridlock Hackathon 2.0. 

All metrics are locked to the final end-to-end execution of the pipeline.

---

## 💻 Slide 1: Cover & The Operational Hook
*   **Slide Title**: SAARTHI: Spatio-temporal Allocation, Anomaly & Risk Triage for High-impact Incidents
*   **Subtitle**: Event-Driven Congestion Console for Bengaluru Traffic Police (BTP)
*   **Visual Layout**: Dark-themed slide. The left half displays the project title and hackathon metadata. The right half shows a full-screen desktop mockup of the SAARTHI Leaflet map running in dark mode with active heat layers and patrol anchors.
*   **Core Bullet Points**:
    *   **Theme**: Theme 2 — Event-Driven Congestion (Planned & Unplanned)
    *   **Core Delivery**: A lightweight, offline-resilient operations console that predicts, prioritizes, allocates, and learns.
    *   **Status**: Fully built prototype with live browser-side simulation.
*   **Speaker Script (15s)**:
    > *"Good evening, judges. Today, traffic police deployment in Bengaluru is largely experience-driven, and event impacts are not quantified in advance. We built SAARTHI—a complete decision console that predicts traffic risk, quantifies delay in expected congestion-minutes, optimizes patrol and barricading deployment mathematically, and refines itself nightly through an active learning loop."*

---

## 📊 Slide 2: Executive Summary (The Paradigm Shift & Counterfactual Moat)
*   **Slide Title**: The Core Paradigm Shift: Congestion-Minutes & Supply-Chain Optimization
*   **Visual Layout**: Bold comparison layout. 
    *   *Left*: "Conventional Systems: Count Events" (red X)
    *   *Right*: "SAARTHI: Forecast Expected Delay Currency" (green checkmark)
    *   *Bottom Callout Card*: **Impact Moat**: **21.1% of delays prevented** (468,910 min) under historical back-test.
*   **Core Bullet Points**:
    *   **The Delay Currency**: We do not predict incident frequency; we predict **congestion-minutes** (Severity $\times$ Criticality $\times$ Clearance Duration).
    *   **Counterfactual Back-Test**: Back-tests patrol allocations against history; pre-positioning prevents **21.1% of delays**, reaching **57.4%** of escalated incidents.
    *   **The Logistics Playbook**: Applies supply-chain fleet optimization to public safety—forecast demand $\rightarrow$ position patrol fleet $\rightarrow$ trigger feedback.
*   **Speaker Script (30s)**:
    > *"Most approaches try to forecast the raw count of traffic incidents. SAARTHI shifts this paradigm. We forecast expected 'congestion-minutes'—a single physical currency representing cumulative delay. Under historical back-testing, we prove that pre-positioning our patrol fleet would have reached 57% of escalated incidents and prevented 21.1% of all traffic delays—saving nearly 469,000 congestion-minutes."*

---

## 🛡️ Slide 3: Data Integrity: Defusing Hidden Data Traps
*   **Slide Title**: Data Integrity: Defusing the Dataset Traps
*   **Visual Layout**: Split layout with warning alerts (`[!WARNING]`). 
    *   *Left Box*: Trap A (Time Corruption) with a bar chart showing the fake 2 AM IST spike.
    *   *Right Box*: Trap B (Duration Corruption) showing the fake 120–180 minute auto-close duration peak.
*   **Core Bullet Points**:
    *   **Trap A (Time Jitter)**: Stored incident start times spike artificially at 2 AM due to timezone/batch uploads. SAARTHI discards absolute hours and keys on Day-of-Week (DOW) and coarse Day-Part bins.
    *   **Trap B (Auto-Close Artifacts)**: Nearly half of raw clearance durations pile into a synthetic 2–3 hour band due to auto-close scripts. We flag these entries as right-censored, training models only on trustworthy human-resolved signals.
*   **Speaker Script (45s)**:
    > *"A machine learning model is only as good as its data. We identified and defused two massive traps in the Astram log. First, the reporting time is corrupted—showing a fake peak at 2 AM due to timezone tagging and batch uploads. Second, nearly half of raw durations are auto-close artifacts. We resolved both: we collapsed absolute hours into Day-Parts to bypass timezone jitter, and treated the auto-close entries as right-censored data so they cannot skew our predictions."*

---

## ⚙️ Slide 4: Multi-Modal Impact Quantification (CIQ)
*   **Slide Title**: The CIQ Engine: Congestion-Impact Quantifier
*   **Visual Layout**: Centered equation layout:
    $$\text{Impact (Minutes)} = \text{Severity Factor} \times \text{Corridor Criticality} \times \text{Expected Clearance Duration}$$
    *   Below the equation, show three KPI callout cards: Severity, Criticality, and Expected Clearance.
*   **Core Bullet Points**:
    *   **Severity Factor**: Fuses priority (High = 2.0x, Low = 1.0x), closure requests (1.8x), and text signal mined via bilingual NLP (-1 to +1 based on English/Kannada field reports).
    *   **Corridor Criticality**: Dynamic weighting ($1.0 \text{ to } 2.0$) measuring the historical share of severe/closure events on each corridor.
    *   **Expected Clearance**: Expected duration predicted per incident cause.
*   **Speaker Script (30s)**:
    > *"To calculate expected congestion-minutes, we developed the Congestion-Impact Quantifier, or CIQ. It fuses incident priority, closure requirements, and Kannada/English report text using bilingual NLP. It weights this severity by a corridor criticality index—which scales from 1 to 2 to prioritize arterial roads—and multiplies it by the incident's predicted clearance time."*

---

## 📈 Slide 5: Spatio-Temporal Risk Surface Forecasting
*   **Slide Title**: Mapping the City's Risk Surface
*   **Visual Layout**: Left: Risk surface heatmap displaying high-density hot zones in Bengaluru. Right: Validation metrics.
*   **Core Bullet Points**:
    *   **Grid Panel Model**: Aggregates the city into a spatial grid of 241 cells ($~1.3\text{ km}$ resolution) tracked across DOW and Day-Parts.
    *   **Risk Model**: Uses a `HistGradientBoostingRegressor` to predict expected daily congestion-minutes per cell.
    *   **Strict Time Validation**: Evaluated on 30 completely unseen days. The top 20% highest-risk cells capture **67.5%** of all actual next-month congestion-minutes (outperforming the cell-mean baseline of 66.1%).
*   **Speaker Script (45s)**:
    > *"Our predictive core models the city as a spatio-temporal panel. We segment Bengaluru into 241 cells and train a Histogram Gradient Boosting Regressor to predict the expected daily congestion-minutes for every cell. Validated on 30 completely unseen days, deploying to the top 20% of cells flagged by our model captures 67.5% of the next month's real congestion, outperforming static historical baselines."*

---

## ⏱️ Slide 6: Clearance Time Prediction (Quantile Models)
*   **Slide Title**: Quantile Models for Patrol Unit Commitment Time
*   **Visuals**: A horizontal bar chart showing P50 (typical) vs. P90 (worst-case) clearance hold times by cause (Protest: 142m / 396m; Public Event: 112m / 332m; Construction: 43m / 315m; Tree Fall: 20m / 296m).
*   **Core Bullet Points**:
    *   **Quantile Regressors**: Separate gradient boosters trained on Quantile Loss at $q=0.5$ (median typical) and $q=0.9$ (worst-case plan-for).
    *   **Commitment Sizing**: Tells dispatchers exactly how long a unit will be tied up at a scene (e.g., protest hold $\le$ 396m).
    *   **Accuracy Lift**: Achieves a **32.8% lower MAE** (Mean Absolute Error) compared to flat historical averages.
*   **Speaker Script (40s)**:
    > *"When an incident occurs, dispatchers need to know how long a patrol unit will be committed. Instead of a flat average, we train censoring-aware quantile regressors. This outputs a P50 typical hold time and a P90 worst-case planning time per cause. For example, a protest has a P50 of 142 minutes but a P90 of 396 minutes. This quantile modeling reduces prediction error by 32.8% over flat averages."*

---

## 📍 Slide 7: Prescriptive Patrol Pre-Positioning & Sizing
*   **Slide Title**: Patrol Pre-Positioning: Location-Allocation & Manpower Sizing
*   **Visual Layout**: Left: Leaflet map view showing optimized unit locations (teal dots 1–8) with their 2.5 km coverage radii. Right: Allocation rules.
*   **Core Bullet Points**:
    *   **Greedy Max-Coverage**: Solves the location-allocation problem. Selects $K$ coordinates that cover the maximum expected congestion-minutes.
    *   **Spatial Constraints**: Units are restricted to a maximum reach of 2.5 km and enforced with a minimum separation of 1.8 km to prevent redundant stacking.
    *   **Sizing Curve**: Shows the exact coverage curve (6 units $\rightarrow$ 50% coverage, 10 units $\rightarrow$ 70%, 14 units $\rightarrow$ 80% coverage).
*   **Speaker Script (45s)**:
    > *"To allocate manpower, we solve a greedy max-coverage location-allocation problem. The model determines the optimal coordinates for $K$ patrol anchors to cover the maximum predicted risk. We enforce a 2.5 km operational reach and a 1.8 km separation constraint to ensure units are spread out. Crucially, we build a resource sizing curve: 6 units capture 50% of congestion-minutes, 10 units cover 70%, and 14 units hit 80%."*

---

## ⛓️ Slide 8: Corridor Spillover Cascade Networks & Diversions
*   **Slide Title**: Mined Corridor Spillovers & Cascading Impact
*   **Visual Layout**: A directed network graph showing corridors (nodes) and spillover probabilities (edges). Highlight Hosur Road pointing to IRR/Thanisandra.
*   **Core Bullet Points**:
    *   **Cascade Association Mining**: Identifies temporal-spatial propagation where an incident on corridor A triggers a cascade on corridor B within 90 minutes.
    *   **Top Edge Cascades**: Mapped strongest transition: **Hosur Road $\rightarrow$ IRR/Thanisandra at $28.5\times$ normal odds** (167 observed cascades).
    *   **System Amplification**: Measures direct vs. derived impact. E.g., Hosur Road: 103k direct + 85k cascaded = 188k total system impact ($1.82\times$ amplification).
*   **Speaker Script (45s)**:
    > *"Instead of viewing corridors in isolation, we mined the logs to build a directed spillover network. We track how gridlock propagates across Bengaluru's geometry. Our model reveals that a choke on Hosur Road triggers follow-on delays on Thanisandra at 28.5 times normal odds. By calculating these cascades, we show that Hosur Road's true systemic cost is 1.82 times its direct delay, highlighting the critical corridors that command immediate triage."*

---

## 🚧 Slide 9: Precision Barricading & Emerging-Event Alarms
*   **Slide Title**: Precision Barricading & Spatio-Temporal Burst Alarms
*   **Visual Layout**: Split layout.
    *   *Left Box*: Ranked list of barricade locations showing approaches, junctions, and points.
    *   *Right Box*: Alarm log catching the March 7 rain flooding event in real time.
*   **Core Bullet Points**:
    *   **Barricade Recommender**: Clusters segment approaches into ranked barricade zones. Recommends exact junctions (K R Circle, Police Corner, K R Market), point counts (2–4), and parallel diversion routes.
    *   **Emerging-Event Alarm**: spatial burst scanner ($\ge 4$ incidents in 1.5 km / 90 min). Caught the March 7 city-wide rain flooding bursts live.
*   **Speaker Script (40s)**:
    > *"For closures, SAARTHI clusters historical segment approaches into persistent barricade zones. It recommends the exact named junction—like K R Circle or K R Market—and the number of physical barricade points. For unplanned events, we run an emerging-event spatial burst scanner. It flags clusters of 4 or more incidents within a 90-minute window, which successfully caught the March 7 rain flooding live."*

---

## 🌐 Slide 10: Prototype Verification, Equity & Retraining
*   **Slide Title**: Deployed Prototype, Equity Lens & Walk-Forward Retraining
*   **Visual Layout**: Left: Screenshot of the live Vercel dashboard showing the counterfactual card and equity lens. Right: Retraining weekly capture rate over 13 weeks.
*   **Core Bullet Points**:
    *   **The Prototype**: Live on [Vercel](https://saarthi-traffic-allocator.vercel.app/) and fully offline-ready locally.
    *   **Equity Lens**: Exposes the reach gap (**84.6 pts**) between central and peripheral zones.
    *   **Retraining Loop**: Re-fits the model weekly on past logs only; risk capture remains stable at **64.7% mean** over 13 weeks.
    *   **Limitations (Stated Honestly)**: Spillovers show correlation, not causation; clearance data is sparse; counterfactual assumes a simplified preventable rate.
*   **Speaker Script (45s)**:
    > *"SAARTHI is a live tool deployed at saarthi-traffic-allocator.vercel.app and fully operational offline. We built an equity lens that exposes our geographical reach gap of 84.6 points. To ensure the model remains stable, a walk-forward loop re-trains the model weekly, keeping risk capture stable at 64.7% mean. We state our limits honestly: spillovers show co-occurrence correlation, and the counterfactual assumes a simplified preventable rate. We show our blind spots because credibility matters. Thank you."*
