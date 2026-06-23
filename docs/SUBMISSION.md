# SAARTHI
### Spatio-temporal Allocation, Anomaly & Risk Triage for High-impact Incidents
**Gridlock Hackathon 2.0 · Theme 2 — Event-Driven Congestion (Planned & Unplanned)**

---

## The one-line thesis
Most teams will forecast *how many* events happen. We forecast **expected
congestion-minutes** — one physical currency — and then **optimally pre-position
scarce enforcement units against it**. That single reframe answers all three of the
problem statement's asks in one system: forecast impact → recommend manpower /
barricading / diversion → learn after every event.

---

## Requirement coverage — every word of the problem statement

| Problem-statement requirement | Status | Where it lives |
|---|---|---|
| Forecast event-related traffic **impact** | ✅ | CIQ congestion-minutes + spatio-temporal risk model (68.7% capture @ top-20%, unseen days) |
| Recommend optimal **manpower** | ✅ | Pre-positioning optimizer + clearance hold-time (P50/P90) + coverage curve |
| Recommend **barricading** | ✅ | Barricade-zone recommender: lat/lon + junction + points + diversion |
| Recommend **diversion plans** | ✅ | Corridor spillover network → reroute outside the blast radius |
| Gap: "impact not quantified in advance" | ✅ | CIQ + planned-event archetype impacts |
| Gap: "deployment is experience-driven" | ✅ | Data-driven optimizer replaces gut-feel |
| Gap: "no post-event learning system" | ✅ | Walk-forward learning loop, proven over 13 weeks (code, not claim) |
| Event type: rallies / protests | ✅ | Protest archetype + spillover |
| Event type: festivals | ✅ | Emerging-event alarm caught the Apr-3 festival; abnormal-day detector |
| Event type: sports | ✅ | Chinnaswamy cricket/IPL archetype |
| Event type: construction | ✅ | Metro / infra-works archetypes (highest planned impact) |
| Event type: sudden gatherings | ✅ | Spatio-temporal burst alarm (Mar-7 rain event caught live) |

Nothing in the brief is left unaddressed.

---


The Astram log is not a congestion time-series — it is **8,173 traffic-police
incident records** (Nov 2023 → Apr 2024). Reading it carefully exposes two traps
that quietly break the naive "count the events per hour" approach:

**Trap A — Time is corrupted.** Raw hour-of-day peaks at **2 AM IST** with the
evening rush nearly empty. That is not reality; it is mixed timezone tagging plus a
2 AM batch-creation spike. Any model keyed on absolute hour learns noise. We **drop
raw hour** and key only on the signals that survive scrutiny: day-of-week, month,
and a coarse day-part.

**Trap B — Clearance time is mostly synthetic.** `closed_datetime` is largely a
batch auto-close that piles "durations" into a fake 2–3 hour band. The obvious
"average clearance time" feature is therefore an artifact. We **flag those rows as
right-censored** and learn clearance time only from the trustworthy signal.

Catching these is the credibility kill-shot: teams that miss them will present
confident models trained on garbage.

---

## Architecture — Predict → Quantify → Prescribe → Learn

1. **Data spine.** Cleans 46 messy columns, canonicalises time, flags both traps,
   and mines the noisy **Kannada + English** field reports for a true-impact signal
   (reports literally say "traffic normal sir" vs "traffic slow / block").

2. **CIQ — Congestion-Impact Quantifier.** Every incident is scored in
   congestion-minutes = severity (priority × road-closure × text-signal) ×
   data-driven corridor-criticality × expected clearance time. **2.55M
   congestion-minutes** quantified across the window.

3. **Clearance model (censoring-aware).** Quantile gradient-boosting predicts P50
   (typical) and P90 (plan-for) hold time per incident — i.e. *how long to commit a
   unit*. **44.1 min MAE vs 65.6 min baseline → 33% better**, on 30 unseen days.

4. **Spatio-temporal risk forecaster.** Gradient-boosting over a 241-cell grid ×
   day-of-week predicts the expected congestion-minute surface. Validated by the
   metric that actually matters operationally — **capture rate: deploy to the top
   20% of cells and catch 68.7% of the next month's real congestion-minutes**
   (vs 66.1% baseline), on unseen days.

5. **Planned-event track.** Parses field reports into archetypes (Metro works,
   cricket/IPL at Chinnaswamy, religious processions, NHAI/BWSSB closures, VIP, rally)
   → a deterministic impact calendar. Counterintuitive finding judges remember:
   **Metro construction is the single highest-impact planned archetype (1,247
   congestion-min median) — louder than cricket.**

6. **Pre-positioning optimizer.** Greedy max-coverage places K patrol anchors to
   maximise covered congestion-minutes. Headline: **8 anchors cover ~61–65% of
   expected congestion-minutes per day** — a real "do more with less" result, with a
   distinct plan for every day of the week.

7. **Corridor spillover network + diversion recommender (the moat).** We mine the
   log for *propagation*: an incident on corridor A triggering a follow-on on a
   nearby corridor B within 90 min. This yields a directed cascade graph — e.g.
   **Hosur Road → IRR/Thanisandra fires at 28× chance (167 observed cascades)**,
   ORR North 1 → Hennur at 17×. For any choked corridor we then recommend reroutes
   onto the nearest *parallel* corridors that are **not** in its blast radius (Mysore
   Road chokes → divert via ORR West / Magadi Road). This is the PS's third ask —
   "diversion plans" — solved on the road network, not as points on a map. No
   points-only approach can produce it.

8. **Marginal coverage curve.** Answers the resource question directly: **6 units →
   50%, 10 → 70%, 14 → 80%** of expected congestion-minutes. Lets BTP size the
   force to a target, not guess.

9. **Abnormal-day detector.** Flags days that deviate from their same-weekday
   baseline (z-score). It is not just a metric — it **caught real events**: it
   flagged **3 Apr 2024 (z=3.0)**, which was a religious festival, and several BWSSB
   work surges. This is the unannounced-event early warning the unplanned track needs.

10. **Barricading recommender.** The PS's third recommendation output, built for
   real: every closure-required incident has two road-segment approaches; we cluster
   those approaches into persistent barricade zones, rank by frequency × impact, and
   attach the named junction (K R Circle, K R Market, Silk Board…), the triggering
   event types, the recommended diversion corridor, and the number of physical
   barricade points. Specific lat/lon barricade locations, not a heuristic table.

11. **Post-event learning loop — implemented and proven, not just claimed.**
   `saarthi_ops.py` runs a **walk-forward** evaluation: each week the risk model
   re-fits on *past data only* and is scored on the *next unseen week*. Over 13
   weeks the capture@20% rises and holds — **60.6% → 69.0%, mean 64.9%** — proving
   the nightly re-fit generalises and isn't overfit. The same routine is the
   operational nightly update: ingest the day's incidents → re-fit → emit a fresh
   plan. (Earlier drafts *claimed* this without code; it is now real.)

12. **Sudden-gathering / emerging-event alarm.** A spatio-temporal scan flags
   ≥4 incidents within 1.5 km / 90 min — the live signature of a forming crowd or
   weather event. Crucially it is **artifact-robust**: it rejects single-cause infra
   surveys (the 2 AM pothole batch) using the *same* Trap-A awareness, so it fires on
   real events — e.g. it caught the **7 Mar 2024 city-wide rain flooding** across
   CBD, Bellary Road and beyond, confirmed by the Kannada field text ("heavy rain /
   tree fall"). This covers the "sudden gatherings" event type explicitly.

---

## Why this wins both judging rooms
- **BTP** gets a deployable decision tool for their hardest unscripted problem:
  *open console → see today's risk surface → get a recommended 8-unit plan + hold
  times → after the event, the model refines itself.*
- **Flipkart** recognises its own playbook: forecast demand → position fleet →
  optimise → feedback. The OR pre-positioning layer is engineering they respect and
  that no solo competitor will build.

---

## What the prototype delivers (in this submission)
- **[Live Vercel Console](https://saarthi-traffic-allocator.vercel.app/)** *(Optimized for Desktop/Laptops)* — Self-contained, **interactive ops console** (`index.html`). Beyond the static views, it now includes a **What-if simulator** (pick a planned event — cricket at Chinnaswamy, Metro works, a protest — and the optimizer re-runs *live in the browser* to re-place units for that day), **urgency tiers** colour-coding every recommendation by response cadence (≤15 min / ≤1 hr / standard / pre-positioned), and a derived **cascade total** on spillover-click (e.g. Hosur Road: 103k direct + 85k cascaded = 188k total system impact, ×1.82).
- Pipeline (run in order): `src/1_pipeline.py` → `src/2_models.py` → `src/3_network.py` → `src/4_ops.py` → `src/5_scenarios.py` → `src/5b_impact.py` → `src/6_dashboard.py` (orchestrated end-to-end via `run_all.py`). Each stage writes what the next reads.
- `dashboard_data.json` and the CSV feeds — clean, machine-readable.

---

## 90-second demo script
1. **Hook (15s):** "Bengaluru's traffic police deploy by gut feel. We turned this
   raw incident log into a deployment console — but first we had to defuse two traps
   that would have sunk a naive model." *(point at the 2 AM peak / fake-duration callout)*
2. **Currency (15s):** "We don't count events. We measure **congestion-minutes** —
   2.55 million of them mapped across the city." *(KPI strip)*
3. **The map (25s):** "This heat surface is a validated forecast — its top 20% of
   cells capture **69% of next month's real congestion**. The teal numbered pins are
   our recommended 8-unit deployment. Switch the day…" *(click Sun → coverage
   recomputes live)* "…and the plan re-optimises. Eight anchors, ~64% coverage."
4. **Diversion — the moat (20s):** "Turn on the spillover net and click Hosur
   Road. The data shows it cascades into Thanisandra at **28× normal odds** — so we
   route traffic *green*, around the blast radius. That's a diversion plan no
   points-on-a-map model can produce."
5. **Hold time + anomaly (15s):** "Each unit gets a hold time — a protest 6+ hours,
   a pothole 7 minutes. And our anomaly detector flagged April 3rd as abnormal —
   there was a festival that day. The system sees unannounced events early."
6. **Barricading + learning (15s):** "For closures we recommend exact barricade
   points — at K R Market, two approaches, divert via ORR West. And this isn't
   static: the learning panel shows the model re-fitting every week on past data
   only, capture climbing to 69% — the nightly loop, proven over 13 weeks."
7. **What-if (15s):** "And it's a tool, not a report. Pick 'Cricket at
   Chinnaswamy' on Thursday — watch a unit pull to the stadium and the plan
   re-optimise live, with a hold time of 83 minutes. A commander runs this before
   the match."
8. **Close (10s):** "Forecast → quantify → pre-position → barricade → divert →
   learn — with two data traps defused. That's SAARTHI."

---

## Honest limits / next steps
- Spillover lift is a temporal+spatial co-occurrence signal (correlation, validated
  against arterial geometry), not proven causation — a routed road-network graph is
  the rigorous upgrade.
- Risk-model gain over the cell-mean baseline is modest on raw error (capture is the
  honest operational win); a self-exciting (Hawkes) point process is the next model.
- Clearance ground truth is thin (human-resolved rows are rare); full survival
  analysis with explicit censoring (lifelines) is the next step.
- The learning loop is proven offline by walk-forward; wiring it to a live Astram
  feed is a deployment task, not a modelling one — the same code runs unchanged.
