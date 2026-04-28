#!/usr/bin/env python3
"""
Observable 22 -- Pentachoric Verification Protocol on IBM-noise-calibrated
simulation.

This script wraps the same 19-qubit circuits used for the Willow pre-registration
(imported unchanged from tesseract_quantum_implementation/cirq/) but runs them
through cirq.DensityMatrixSimulator with a uniform depolarising channel tuned
to IBM Eagle r3 / Heron r2 calibrated noise:

    Eagle r3 (ibm_strasbourg, ibm_brussels):  p_depol = 0.005
    Heron r2 (ibm_kingston):                   p_depol = 0.003

The circuits themselves are hardware-topology-agnostic; IBM's heavy-hex
connectivity does NOT introduce SWAP overhead for the triangle observables
(16, 22) the way Willow's square grid does. If anything, IBM should be a
BETTER hardware match for these. The open question the simulation answers is
whether IBM's slightly higher per-gate error (0.003-0.005 vs Willow's target
~0.003) leaves enough fidelity budget for all five pentachoric gates to pass.

Usage
-----
    python sim_obs22_pentachoric_ibm.py --backend heron --n-trials 10 --shots 2048
    python sim_obs22_pentachoric_ibm.py --backend eagle --n-trials 10 --shots 2048

Authors: Stenberg & Hetland with Claude Anthropic, April 2026.
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import cirq

THIS = Path(__file__).resolve()
# Import the canonical circuit builders from tesseract_quantum_implementation
# Local checkout is expected at C:\Users\selin\tesseract_quantum_implementation
TESSERACT_CIRQ = Path(r"C:\Users\selin\tesseract_quantum_implementation\cirq")
if not TESSERACT_CIRQ.exists():
    raise RuntimeError(f"Expected canonical cirq folder at {TESSERACT_CIRQ}")
sys.path.insert(0, str(TESSERACT_CIRQ))

from run_p4s_tesseract_memory_cirq import (  # noqa: E402
    build_write_read_circuit, build_compute_sustain_circuit,
    LABELS,
)
from run_p4s_cirq import overlap_from_swap  # noqa: E402


IBM_NOISE_PROFILES = {
    "heron":  {"p_depol": 0.003, "label": "Heron r2 (ibm_kingston)"},
    "eagle":  {"p_depol": 0.005, "label": "Eagle r3 (ibm_strasbourg/brussels)"},
    "ideal":  {"p_depol": 0.000, "label": "ideal (noiseless, for sanity check)"},
}


def inject_uniform_depolarize(circuit: cirq.Circuit, p: float) -> cirq.Circuit:
    """Insert a uniform single-qubit depolarising channel after every
    non-measurement operation. Emulates uniform per-gate fidelity."""
    if p <= 0:
        return circuit
    noisy = cirq.Circuit()
    for moment in circuit:
        noisy.append(moment)
        # One depolarising hit per qubit touched in this moment
        touched = set()
        for op in moment.operations:
            if isinstance(op.gate, cirq.MeasurementGate):
                continue
            for q in op.qubits:
                touched.add(q)
        if touched:
            noisy.append(
                cirq.Moment([cirq.depolarize(p).on(q) for q in touched]))
    return noisy


def run_circuit(qc: cirq.Circuit, p_depol: float, shots: int) -> float:
    """Run a single circuit under IBM noise, return overlap-from-SWAP."""
    if p_depol > 0:
        noisy = inject_uniform_depolarize(qc, p_depol)
        sim = cirq.DensityMatrixSimulator()
        res = sim.run(noisy, repetitions=shots)
    else:
        sim = cirq.Simulator()
        res = sim.run(qc, repetitions=shots)
    zeros = int(res.histogram(key="anc").get(0, 0))
    return overlap_from_swap(zeros, shots)


# -- Stage helpers ----------------------------------------------------------
def stage_S_substrate(n_compute: int, J_intra: float, p_depol: float,
                        shots: int, n_trials: int):
    out = {L: {m: [] for m in "ABC"} for L in LABELS}
    print(f"  [S] substrate: compute triangle self-sustain")
    for label in LABELS:
        for merkabit in "ABC":
            for _ in range(n_trials):
                qc = build_compute_sustain_circuit(
                    label, label, label, n_compute, J_intra, merkabit)
                out[label][merkabit].append(run_circuit(qc, p_depol, shots))
    flat = [v for L in LABELS for m in "ABC" for v in out[L][m]]
    mean = float(np.mean(flat))
    print(f"      mean |<u|v>| = {mean:.4f} across 3 merkabits x 3 labels")
    return out, mean


def stage_R_rotation(n_compute: int, J_intra: float, J_mem: float,
                      p_depol: float, shots: int, n_trials: int,
                      apply_tunnel: bool = True, readout: str = "v_D"):
    F = {X: {Y: [] for Y in LABELS} for X in LABELS}
    for X in LABELS:
        for Y in LABELS:
            for _ in range(n_trials):
                qc = build_write_read_circuit(
                    X, X, X, Y, n_compute, J_intra, J_mem,
                    apply_memory_tunnel=apply_tunnel, readout=readout)
                F[X][Y].append(run_circuit(qc, p_depol, shots))
    matrix = np.array([[np.mean(F[X][Y]) for Y in LABELS] for X in LABELS])
    return F, matrix


def cycled_gap(matrix):
    # cycle: alpha -> gamma (0,2), beta -> alpha (1,0), gamma -> beta (2,1)
    cycled = [(0, 2), (1, 0), (2, 1)]
    M = np.asarray(matrix)
    c = np.array([M[i, j] for i, j in cycled])
    mask = np.ones(9, dtype=bool)
    for i, j in cycled:
        mask[3 * i + j] = False
    off = M.flatten()[mask]
    gap = float(c.mean() - off.mean())
    sem = float(np.sqrt(c.std(ddof=1)**2 / 3 + off.std(ddof=1)**2 / 6))
    sigma = gap / sem if sem > 0 else float("inf")
    return float(c.mean()), float(off.mean()), gap, sigma


# -- Thresholds (identical to Willow repo) ---------------------------------
THRESHOLDS = {
    "S_mean_low":       0.30,
    "S_mean_high":      0.65,
    "R_gap_min":        0.08,
    "R_sigma_min":      2.0,
    "T_null_tol":       0.03,
    "F_peak_low":       0.30,
    "F_peak_high":      0.70,
    "P_chirality_tol":  0.03,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=list(IBM_NOISE_PROFILES.keys()),
                     default="heron",
                     help="IBM noise profile: heron / eagle / ideal")
    ap.add_argument("--n-trials", type=int, default=10)
    ap.add_argument("--shots", type=int, default=2048)
    ap.add_argument("--n-compute", type=int, default=1)
    ap.add_argument("--J-intra", type=float, default=0.1)
    ap.add_argument("--J-mem", type=float, default=0.5)
    ap.add_argument("--skip-F-sweep", action="store_true",
                     help="skip Stage 4 frequency sweep (speeds up run)")
    args = ap.parse_args()

    profile = IBM_NOISE_PROFILES[args.backend]
    p_depol = profile["p_depol"]
    print(f"\nOBSERVABLE 22 -- Pentachoric Verification Protocol (IBM sim)")
    print(f"  backend:   {profile['label']}")
    print(f"  p_depol:   {p_depol}")
    print(f"  n_trials:  {args.n_trials}")
    print(f"  shots:     {args.shots}")
    print(f"  J_intra:   {args.J_intra}, J_mem: {args.J_mem}")
    print()

    # --- STAGE 1 (S) ------------------------------------------------------
    s1_raw, s_mean = stage_S_substrate(
        args.n_compute, args.J_intra, p_depol, args.shots, args.n_trials)
    s_pass = THRESHOLDS["S_mean_low"] <= s_mean <= THRESHOLDS["S_mean_high"]
    print(f"      22-S: {'PASS' if s_pass else 'FAIL'}  "
          f"(range {THRESHOLDS['S_mean_low']}-{THRESHOLDS['S_mean_high']})")

    # --- STAGE 2 (R) ------------------------------------------------------
    print(f"\n  [R] rotation: 3x3 write-read at J_mem={args.J_mem}")
    r_raw, r_matrix = stage_R_rotation(
        args.n_compute, args.J_intra, args.J_mem, p_depol,
        args.shots, args.n_trials, apply_tunnel=True, readout="v_D")
    r_cycled, r_off, r_gap, r_sigma = cycled_gap(r_matrix)
    print(f"      cycled mean   = {r_cycled:.4f}")
    print(f"      off mean      = {r_off:.4f}")
    print(f"      cycled gap    = {r_gap:+.4f}  ({r_sigma:+.2f} sigma)")
    r_pass = (r_gap >= THRESHOLDS["R_gap_min"]
               and r_sigma >= THRESHOLDS["R_sigma_min"])
    print(f"      22-R: {'PASS' if r_pass else 'FAIL'}")

    # --- STAGE 3 (T) ------------------------------------------------------
    print(f"\n  [T] transfer null: no memory tunnel")
    t_raw, t_matrix = stage_R_rotation(
        args.n_compute, args.J_intra, args.J_mem, p_depol,
        args.shots, args.n_trials, apply_tunnel=False, readout="v_D")
    t_cycled, t_off, t_gap, t_sigma = cycled_gap(t_matrix)
    print(f"      cycled gap (no tunnel) = {t_gap:+.4f}")
    t_pass = abs(t_gap) <= THRESHOLDS["T_null_tol"]
    print(f"      22-T: {'PASS' if t_pass else 'FAIL'}  "
          f"(|.|<={THRESHOLDS['T_null_tol']})")

    # --- STAGE 4 (F) ------------------------------------------------------
    if args.skip_F_sweep:
        print(f"\n  [F] frequency sweep: SKIPPED (--skip-F-sweep)")
        f_pass = None
        f_sweep = None
        f_peak = None
    else:
        print(f"\n  [F] frequency: sweep J_mem in {{0.0, 0.25, 0.5, 0.75, 1.0}}")
        sweep = []
        for J in [0.0, 0.25, 0.5, 0.75, 1.0]:
            _, mat = stage_R_rotation(
                args.n_compute, args.J_intra, J, p_depol,
                args.shots, args.n_trials, apply_tunnel=True, readout="v_D")
            _, _, gap, _ = cycled_gap(mat)
            sweep.append({"J_mem": J, "gap": gap})
            print(f"      J_mem={J:.2f}  gap={gap:+.4f}")
        f_peak = max(sweep, key=lambda d: abs(d["gap"]))
        f_pass = THRESHOLDS["F_peak_low"] <= f_peak["J_mem"] <= THRESHOLDS["F_peak_high"]
        f_sweep = sweep
        print(f"      peak at J_mem={f_peak['J_mem']}  gap={f_peak['gap']:+.4f}")
        print(f"      22-F: {'PASS' if f_pass else 'FAIL'}")

    # --- STAGE 5 (P) ------------------------------------------------------
    print(f"\n  [P] phase/cross-chirality: read u_D directly")
    p_raw, p_matrix = stage_R_rotation(
        args.n_compute, args.J_intra, args.J_mem, p_depol,
        args.shots, args.n_trials, apply_tunnel=True, readout="u_D")
    p_cycled, p_off, p_gap, p_sigma = cycled_gap(p_matrix)
    # For cross-chirality we expect the gap to be near zero (u_D unaffected)
    diag = float(np.mean([p_matrix[i, i] for i in range(3)]))
    off = float(np.mean([p_matrix[i, j] for i in range(3) for j in range(3) if i != j]))
    p_diag_off_gap = diag - off
    p_pass = abs(p_diag_off_gap) <= THRESHOLDS["P_chirality_tol"]
    print(f"      u_D diag mean = {diag:.4f},  off-diag mean = {off:.4f}")
    print(f"      diag-off gap  = {p_diag_off_gap:+.4f}")
    print(f"      22-P: {'PASS' if p_pass else 'FAIL'}  "
          f"(|.|<={THRESHOLDS['P_chirality_tol']})")

    # --- VERDICT ----------------------------------------------------------
    passes = {
        "S": bool(s_pass), "R": bool(r_pass), "T": bool(t_pass),
        "F": bool(f_pass) if f_pass is not None else None, "P": bool(p_pass),
    }
    if all(p is not False for p in passes.values()) and all(
            p is True for p in passes.values() if p is not None):
        verdict = "STRONG PASS (all five pentachoric gates passed)"
    elif s_pass and r_pass and p_pass:
        verdict = ("WEAK PASS (substrate + rotation + cross-chirality pass; "
                   "T or F degraded or skipped)")
    else:
        failed = [k for k, v in passes.items() if v is False]
        verdict = f"NULL (failed gates: {', '.join(failed)})"
    print(f"\n  PENTACHORIC VERDICT ({args.backend}): {verdict}")

    # --- Save JSON --------------------------------------------------------
    outdir = Path(__file__).parent / "outputs"
    outdir.mkdir(exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    fname = outdir / f"obs22_pentachoric_ibm_{args.backend}_{stamp}.json"
    payload = {
        "observable":   "obs22_pentachoric_ibm",
        "backend":      profile["label"],
        "p_depol":      p_depol,
        "parameters":   vars(args),
        "thresholds":   THRESHOLDS,
        "measurement": {
            "S_mean":        s_mean,
            "S_pass":        bool(s_pass),
            "R_matrix":      r_matrix.tolist(),
            "R_cycled_mean": r_cycled,
            "R_off_mean":    r_off,
            "R_gap":         r_gap,
            "R_sigma":       r_sigma,
            "R_pass":        bool(r_pass),
            "T_matrix":      t_matrix.tolist(),
            "T_gap":         t_gap,
            "T_pass":        bool(t_pass),
            "F_sweep":       f_sweep,
            "F_peak":        f_peak,
            "F_pass":        bool(f_pass) if f_pass is not None else None,
            "P_matrix":      p_matrix.tolist(),
            "P_diag":        diag,
            "P_off":         off,
            "P_gap":         p_diag_off_gap,
            "P_pass":        bool(p_pass),
        },
        "verdict":      verdict,
        "timestamp":    stamp,
    }
    fname.write_text(json.dumps(payload, indent=2))
    print(f"\n  Wrote {fname}")


if __name__ == "__main__":
    main()
