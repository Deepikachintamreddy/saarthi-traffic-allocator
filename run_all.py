#!/usr/bin/env python3
"""
SAARTHI — run the full pipeline end to end.

    python run_all.py

Stages (each writes what the next reads):
    1_pipeline   clean + CIQ congestion-impact
    2_models     spatio-temporal risk + clearance quantile models
    3_network    spillover cascade + diversion + coverage curve + anomaly
    4_ops        barricading + walk-forward learning + emerging-event alarm
    5_scenarios  what-if simulator feed + cascade totals + urgency tiers
    6_dashboard  build the interactive console -> ./index.html

Override data/output locations with env vars SAARTHI_DATA / SAARTHI_OUT.
"""
import subprocess, sys, time
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
STAGES = ["1_pipeline.py","2_models.py","3_network.py","4_ops.py","5_scenarios.py","6_dashboard.py"]

def main():
    t0 = time.time()
    for i, stage in enumerate(STAGES, 1):
        print(f"\n[{i}/{len(STAGES)}] {stage} ...", flush=True)
        r = subprocess.run([sys.executable, str(SRC / stage)])
        if r.returncode != 0:
            print(f"\n✗ {stage} failed (exit {r.returncode}). Stopping.")
            sys.exit(r.returncode)
    print(f"\n✓ Done in {time.time()-t0:.0f}s. Open ./index.html in a browser.")

if __name__ == "__main__":
    main()
