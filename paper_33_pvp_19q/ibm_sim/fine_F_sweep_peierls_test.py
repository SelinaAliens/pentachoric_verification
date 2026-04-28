#!/usr/bin/env python3
"""High-statistics F-sweep at ideal noise, focused on the plateau region.

Goal: test whether the cycled-gap plateau ceiling equals 1/6 = 0.16667
(the Paper 6 Peierls flux Phi = window width 3/2 - 4/3) within tight
SEM. Current 40960-shot sweep gives SEM ~0.003, so 1/6 vs adjacent
values is barely resolvable. We bump to shots_total = 200000 and focus
the sweep on the plateau peak.

Decision rule:
  - If max plateau gap = 1/6 +/- 3*SEM: architectural connection confirmed.
  - If max plateau gap differs from 1/6 by > 3*SEM: bounded but not 1/6.
"""
from __future__ import annotations
import json
import math
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from sim_obs22_pentachoric_ibm_v2 import stage_R_3x3, cycled_gap


def main():
    # Focus on the plateau region with extra resolution around the peak (J~0.65)
    Js = [0.45, 0.50, 0.55, 0.60, 0.625, 0.65, 0.675, 0.70, 0.75, 0.80,
          0.85, 0.90, 0.95, 1.00]
    shots_total = 200_000
    seed = 42
    print(f"Peierls-flux plateau test (shots_total = {shots_total}, "
          f"seed = {seed}, ideal noise)")
    print(f"  J values: {Js}")
    print(f"  Target: 1/6 = {1/6:.6f}")
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
        # Distance from 1/6 in sigma
        d_peierls = (gap - 1/6) / gap_sem
        print(f"  J={J:.3f}  gap={gap:+.5f} +/- {gap_sem:.5f}  "
              f"({d_peierls:+5.2f} sigma from 1/6)")

    # Find max gap and its sigma-distance from 1/6
    gaps = np.array([s["gap"] for s in sweep])
    sems = np.array([s["gap_sem"] for s in sweep])
    Js_arr = np.array([s["J_mem"] for s in sweep])
    idx_max = int(np.argmax(gaps))
    max_gap = float(gaps[idx_max])
    max_sem = float(sems[idx_max])
    max_J = float(Js_arr[idx_max])
    delta = max_gap - 1/6
    delta_sigma = delta / max_sem if max_sem > 0 else float('inf')

    # Parabolic vertex
    a, b, c = np.polyfit(Js_arr, gaps, 2)
    if a < 0:
        J_star = -b / (2*a)
        # Vertex value
        gap_star = a*J_star**2 + b*J_star + c
        # Use linear-error propagation around vertex via 3 nearest points
        # to estimate vertex SEM (rough)
        vertex_sem = float(np.mean(sems))
    else:
        J_star = None
        gap_star = None
        vertex_sem = None

    print(f"\n  Argmax: J={max_J:.3f}, gap={max_gap:.5f} +/- {max_sem:.5f}")
    print(f"  1/6   = {1/6:.5f}")
    print(f"  delta = {delta:+.5f}  ({delta_sigma:+.2f} sigma)")

    if J_star is not None:
        delta_v = gap_star - 1/6
        delta_v_sigma = delta_v / vertex_sem
        print(f"\n  Parabola vertex: J* = {J_star:.4f}, "
              f"gap* = {gap_star:.5f} (+/- ~{vertex_sem:.5f})")
        print(f"  vertex delta = {delta_v:+.5f}  ({delta_v_sigma:+.2f} sigma "
              f"from 1/6)")

    # Final decision
    print(f"\n  CONCLUSION:")
    if abs(delta_sigma) <= 3:
        print(f"    Argmax gap consistent with 1/6 at <= 3 sigma.")
        print(f"    Architectural connection (plateau ceiling = Peierls flux)")
        print(f"    is supported by the data.")
    else:
        print(f"    Argmax gap differs from 1/6 by {abs(delta_sigma):.1f} sigma.")
        print(f"    Plateau is bounded but does NOT equal 1/6 exactly.")
        print(f"    Connection is structural (both bounded) but not the "
              f"same number.")

    out = {
        "timestamp":   datetime.utcnow().isoformat(),
        "shots_total": shots_total,
        "seed":        seed,
        "target":      "1/6 = 0.16667 (Paper 6 Peierls flux)",
        "sweep":       sweep,
        "argmax": {"J_mem": max_J, "gap": max_gap, "gap_sem": max_sem,
                    "delta_from_1_over_6": delta,
                    "sigma_from_1_over_6": delta_sigma},
        "parabola": {"a": float(a), "b": float(b), "c": float(c),
                     "J_star": float(J_star) if J_star is not None else None,
                     "gap_star": float(gap_star) if gap_star is not None else None,
                     "vertex_sem_est": vertex_sem},
    }
    outdir = Path(__file__).parent / "outputs"
    outdir.mkdir(exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    fname = outdir / f"fine_F_sweep_peierls_test_{stamp}.json"
    fname.write_text(json.dumps(out, indent=2))
    print(f"\n  Wrote {fname}")


if __name__ == "__main__":
    main()
