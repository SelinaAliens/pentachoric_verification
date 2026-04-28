#!/usr/bin/env python3
"""
Fine F-sweep at ideal noise to map the cycled-gap landscape precisely.

Goal: decide whether the cycled-gap has a sharp peak at some J*, or a
plateau across J in [0.5, 1.0]. This determines whether the F-gate should
be a peak-in-window test or a plateau test.
"""
from __future__ import annotations
import json
import math
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from sim_obs22_pentachoric_ibm_v2 import (
    stage_R_3x3, cycled_gap,
)


def main():
    Js = [0.0, 0.10, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60,
          0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00]
    shots_total = 40960
    seed = 42
    print(f"Fine F-sweep at ideal noise")
    print(f"  J values:    {Js}")
    print(f"  shots_total: {shots_total}")
    print(f"  seed:        {seed}")
    print()

    sweep = []
    for J in Js:
        mat, sem = stage_R_3x3(
            n_compute=1, J_intra=0.1, J_mem=J,
            p1q=0.0, p2q=0.0, p_meas=0.0,
            shots_total=shots_total,
            apply_tunnel=True, readout="v_D", seed=seed)
        cyc, off, gap, gap_sem, sigma = cycled_gap(mat, sem)
        sweep.append({"J_mem": J, "cycled": cyc, "off": off,
                       "gap": gap, "gap_sem": gap_sem, "sigma": sigma})
        print(f"  J={J:.2f}  cyc={cyc:.4f}  off={off:.4f}  "
              f"gap={gap:+.4f} +/- {gap_sem:.4f}  ({sigma:+.1f} sigma)")

    # Parabola fit (in case of peak); also report flat-plateau test
    Js_arr = np.array([s["J_mem"] for s in sweep])
    gaps = np.array([s["gap"] for s in sweep])
    sems = np.array([s["gap_sem"] for s in sweep])

    a, b, c = np.polyfit(Js_arr, gaps, 2)
    J_star = -b / (2*a) if a != 0 else None
    print(f"\n  parabola fit: gap = {a:+.4f} J^2 + {b:+.4f} J + {c:+.4f}")
    if a < 0 and J_star is not None:
        print(f"  vertex (peak) at J* = {J_star:.3f}")
    else:
        print(f"  parabola not concave-down (a={a:.4f}); no clear peak")

    # Plateau test: count J values in [0.5, 1.0] with gap >= 0.10
    plateau_mask = (Js_arr >= 0.5) & (Js_arr <= 1.0) & (gaps >= 0.10)
    n_plateau = int(plateau_mask.sum())
    n_in_region = int(((Js_arr >= 0.5) & (Js_arr <= 1.0)).sum())
    print(f"\n  plateau test: {n_plateau}/{n_in_region} J values in "
          f"[0.5, 1.0] have gap >= 0.10")
    plateau_max = float(gaps[(Js_arr >= 0.5) & (Js_arr <= 1.0)].max())
    plateau_min = float(gaps[(Js_arr >= 0.5) & (Js_arr <= 1.0)].min())
    plateau_range = plateau_max - plateau_min
    print(f"  plateau range: max={plateau_max:.4f}, min={plateau_min:.4f}, "
          f"span={plateau_range:.4f}")

    # Save
    out = {
        "timestamp": datetime.utcnow().isoformat(),
        "shots_total": shots_total, "seed": seed,
        "sweep": sweep,
        "parabola": {"a": float(a), "b": float(b), "c": float(c),
                     "J_star": float(J_star) if J_star is not None else None,
                     "concave_down": bool(a < 0)},
        "plateau": {"n_above_010_in_region": n_plateau,
                    "n_in_region": n_in_region,
                    "max_gap": plateau_max,
                    "min_gap": plateau_min,
                    "range": plateau_range},
    }
    outdir = Path(__file__).parent / "outputs"
    outdir.mkdir(exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    fname = outdir / f"fine_F_sweep_ideal_{stamp}.json"
    fname.write_text(json.dumps(out, indent=2))
    print(f"\n  Wrote {fname}")


if __name__ == "__main__":
    main()
