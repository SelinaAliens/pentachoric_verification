#!/usr/bin/env python3
"""
Observable 22 (v2) -- Pentachoric Verification Protocol on IBM-noise-calibrated
simulation, with corrected statistics and more realistic noise model.

Improvements over v1 (sim_obs22_pentachoric_ibm.py, pre-registered at c8521bb):

  1. Single big-shots run per cell. The v1 trial loop is statistically void
     under cirq.DensityMatrixSimulator: trials sample the same deterministic
     density matrix, so n_trials*shots independent samples are equivalent to
     1 trial * (n_trials*shots) shots, and trial-std underestimates SEM.
     We collapse to a single shots_total run and report binomial shot SEM.

  2. Per-cell SEM is propagated into the cycled-gap SEM (instead of the
     across-trial std heuristic).

  3. Two-qubit gates get a separately scaled depolarising channel
     (default p_2q = 5 * p_1q). The v1 model used a single uniform p for
     all qubits touched in any moment, which under-stresses iSWAP^J chains.

  4. Measurement readout bit-flip error on the SWAP-test ancilla
     (default 0.7%, IBM-typical).

  5. Comparative F-gate criterion: parabolic fit of gap(J_mem) and check
     vertex in (0.30, 0.70); plus a structural test "partial SWAP beats
     full SWAP" using gap(0.5) - gap(1.0). Both criteria are saved.

  6. Optional fine F-sweep (--fine-sweep adds J in {0.4, 0.45, 0.55, 0.6}).

  7. Reproducibility: --seed propagates to numpy and cirq simulators.

The pre-registered v1 script at c8521bb is left UNTOUCHED. This v2 is a
methodological correction layer; results from v2 should be reported as
distinct from the pre-registered v1 numbers.

Usage
-----
    python sim_obs22_pentachoric_ibm_v2.py --backend heron --shots-total 20480
    python sim_obs22_pentachoric_ibm_v2.py --backend eagle --shots-total 20480 --fine-sweep
    python sim_obs22_pentachoric_ibm_v2.py --backend ideal  # sanity check

Authors: Stenberg with Claude Anthropic (v2 correction layer), April 2026.
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
TESSERACT_CIRQ = Path(r"C:\Users\selin\tesseract_quantum_implementation\cirq")
if not TESSERACT_CIRQ.exists():
    raise RuntimeError(f"Expected canonical cirq folder at {TESSERACT_CIRQ}")
sys.path.insert(0, str(TESSERACT_CIRQ))

from run_p4s_tesseract_memory_cirq import (  # noqa: E402
    build_write_read_circuit, build_compute_sustain_circuit, LABELS,
)
from run_p4s_cirq import overlap_from_swap  # noqa: E402


# IBM calibration-ish defaults. p1q = single-qubit depol; p2q = two-qubit
# (and three-qubit) depol; p_meas = measurement bit-flip on the ancilla.
# These approximate vendor-published medians; precise per-qubit calibration
# requires Qiskit Aer FakeKingston / FakeSherbrooke and is left for a third
# revision.
IBM_NOISE_PROFILES = {
    "heron": {"p1q": 0.0003, "p2q": 0.005,  "p_meas": 0.007,
              "label": "Heron r2 (ibm_kingston)"},
    "eagle": {"p1q": 0.0005, "p2q": 0.012,  "p_meas": 0.013,
              "label": "Eagle r3 (ibm_strasbourg/brussels)"},
    "ibm_legacy_uniform_heron": {"p1q": 0.003, "p2q": 0.003, "p_meas": 0.0,
              "label": "Heron r2 (v1 legacy uniform 0.003)"},
    "ibm_legacy_uniform_eagle": {"p1q": 0.005, "p2q": 0.005, "p_meas": 0.0,
              "label": "Eagle r3 (v1 legacy uniform 0.005)"},
    "ideal": {"p1q": 0.0, "p2q": 0.0, "p_meas": 0.0,
              "label": "ideal (noiseless)"},
}


# ---------------------------------------------------------------------------
# NOISE INJECTION (1q vs 2q+ split, plus measurement readout error)
# ---------------------------------------------------------------------------
def inject_calibrated_noise(circuit: cirq.Circuit, p1q: float, p2q: float,
                              p_meas: float) -> cirq.Circuit:
    """Insert depolarising errors after each non-measurement op (per qubit,
    rate depends on op arity) and a bit-flip immediately before each
    measurement.
    """
    if p1q <= 0 and p2q <= 0 and p_meas <= 0:
        return circuit
    out = cirq.Circuit()
    for moment in circuit:
        meas_qubits = [q for op in moment.operations
                         if isinstance(op.gate, cirq.MeasurementGate)
                         for q in op.qubits]
        if meas_qubits and p_meas > 0:
            out.append(cirq.Moment(
                [cirq.bit_flip(p_meas).on(q) for q in meas_qubits]))
        out.append(moment)
        err_ops = []
        for op in moment.operations:
            if isinstance(op.gate, cirq.MeasurementGate):
                continue
            arity = len(op.qubits)
            p_use = p1q if arity == 1 else p2q
            if p_use > 0:
                for q in op.qubits:
                    err_ops.append(cirq.depolarize(p_use).on(q))
        if err_ops:
            out.append(cirq.Moment(err_ops))
    return out


# ---------------------------------------------------------------------------
# RUN A CIRCUIT, RETURN (overlap, shot SEM)
# ---------------------------------------------------------------------------
def run_circuit(qc: cirq.Circuit, p1q: float, p2q: float, p_meas: float,
                shots_total: int, seed=None) -> tuple[float, float]:
    """Run circuit once with shots_total samples; return (overlap, sem).

    SEM is propagated from the binomial shot variance of P(ancilla=0):
        overlap   = sqrt(2 P0 - 1)
        var(P0)   = P0 (1 - P0) / shots_total
        sem(overlap) = sqrt(var(P0)) / overlap   (delta method)

    For overlap = 0 we report a conservative SEM = sqrt(2 var(P0)).
    """
    is_noisy = (p1q > 0) or (p2q > 0) or (p_meas > 0)
    if is_noisy:
        noisy = inject_calibrated_noise(qc, p1q, p2q, p_meas)
        sim = cirq.DensityMatrixSimulator(seed=seed)
        res = sim.run(noisy, repetitions=shots_total)
    else:
        sim = cirq.Simulator(seed=seed)
        res = sim.run(qc, repetitions=shots_total)
    zeros = int(res.histogram(key="anc").get(0, 0))
    p0 = zeros / shots_total
    p0_var = p0 * (1 - p0) / shots_total
    radicand = 2 * p0 - 1
    if radicand <= 0:
        return 0.0, math.sqrt(max(2 * p0_var, 1e-12))
    overlap = math.sqrt(radicand)
    overlap_sem = math.sqrt(p0_var) / overlap
    return overlap, overlap_sem


# ---------------------------------------------------------------------------
# STAGE HELPERS
# ---------------------------------------------------------------------------
def stage_S_substrate(n_compute: int, J_intra: float, p1q: float, p2q: float,
                       p_meas: float, shots_total: int, seed=None):
    out = {L: {m: None for m in "ABC"} for L in LABELS}
    out_sem = {L: {m: None for m in "ABC"} for L in LABELS}
    print("  [S] substrate: compute triangle self-sustain (3 labels x 3 sites)")
    for label in LABELS:
        for merkabit in "ABC":
            qc = build_compute_sustain_circuit(
                label, label, label, n_compute, J_intra, merkabit)
            m, s = run_circuit(qc, p1q, p2q, p_meas, shots_total, seed=seed)
            out[label][merkabit] = m
            out_sem[label][merkabit] = s
    flat = [out[L][m] for L in LABELS for m in "ABC"]
    flat_sem = [out_sem[L][m] for L in LABELS for m in "ABC"]
    mean = float(np.mean(flat))
    # Mean of 9 measurements with per-cell SEM
    mean_sem = math.sqrt(sum(s**2 for s in flat_sem)) / 9
    print(f"      mean |<u|v>| = {mean:.4f} +/- {mean_sem:.4f}")
    return out, out_sem, mean, mean_sem


def stage_R_3x3(n_compute: int, J_intra: float, J_mem: float, p1q: float,
                  p2q: float, p_meas: float, shots_total: int,
                  apply_tunnel: bool, readout: str, seed=None):
    matrix = np.zeros((3, 3))
    matrix_sem = np.zeros((3, 3))
    for i, X in enumerate(LABELS):
        for j, Y in enumerate(LABELS):
            qc = build_write_read_circuit(
                X, X, X, Y, n_compute, J_intra, J_mem,
                apply_memory_tunnel=apply_tunnel, readout=readout)
            m, s = run_circuit(qc, p1q, p2q, p_meas, shots_total, seed=seed)
            matrix[i, j] = m
            matrix_sem[i, j] = s
    return matrix, matrix_sem


# ---------------------------------------------------------------------------
# CYCLED-GAP METRIC, with proper SEM propagation
# ---------------------------------------------------------------------------
CYCLED_IDX = [(0, 2), (1, 0), (2, 1)]   # alpha->gamma, beta->alpha, gamma->beta


def cycled_gap(matrix: np.ndarray, matrix_sem: np.ndarray):
    M = np.asarray(matrix)
    S = np.asarray(matrix_sem)
    c_vals = np.array([M[i, j] for i, j in CYCLED_IDX])
    c_sems = np.array([S[i, j] for i, j in CYCLED_IDX])
    mask = np.ones((3, 3), dtype=bool)
    for i, j in CYCLED_IDX:
        mask[i, j] = False
    o_vals = M[mask]
    o_sems = S[mask]
    cycled_mean = float(c_vals.mean())
    off_mean = float(o_vals.mean())
    gap = cycled_mean - off_mean
    cycled_mean_sem = math.sqrt(float((c_sems**2).sum())) / 3.0
    off_mean_sem = math.sqrt(float((o_sems**2).sum())) / 6.0
    gap_sem = math.sqrt(cycled_mean_sem**2 + off_mean_sem**2)
    sigma = gap / gap_sem if gap_sem > 0 else float("inf")
    return cycled_mean, off_mean, gap, gap_sem, sigma


def diag_off_gap(matrix: np.ndarray, matrix_sem: np.ndarray):
    """Stage P metric: u_D should not pick up content; diag-off gap ~ 0."""
    M = np.asarray(matrix)
    S = np.asarray(matrix_sem)
    diag = np.array([M[i, i] for i in range(3)])
    diag_s = np.array([S[i, i] for i in range(3)])
    off = np.array([M[i, j] for i in range(3) for j in range(3) if i != j])
    off_s = np.array([S[i, j] for i in range(3) for j in range(3) if i != j])
    gap = float(diag.mean() - off.mean())
    diag_sem = math.sqrt(float((diag_s**2).sum())) / 3.0
    off_sem = math.sqrt(float((off_s**2).sum())) / 6.0
    gap_sem = math.sqrt(diag_sem**2 + off_sem**2)
    return float(diag.mean()), float(off.mean()), gap, gap_sem


# ---------------------------------------------------------------------------
# F-PASS: parabolic fit + structural comparator
# ---------------------------------------------------------------------------
def f_gate_evaluate(sweep, f_low=0.30, f_high=0.70):
    """Return a structured F-gate verdict.

    sweep: list of {"J_mem": float, "gap": float, "gap_sem": float}.
    """
    Js = np.array([d["J_mem"] for d in sweep])
    gaps = np.array([d["gap"] for d in sweep])
    sems = np.array([d.get("gap_sem", 0.0) for d in sweep])

    # Parabolic fit (gap = a J^2 + b J + c). Concave-down a < 0 means a peak.
    fit = {"J_star": None, "a": None, "b": None, "c": None,
            "in_window": False}
    if len(Js) >= 3:
        a, b, c = np.polyfit(Js, gaps, 2)
        fit.update({"a": float(a), "b": float(b), "c": float(c)})
        if a < 0:
            J_star = -b / (2 * a)
            fit["J_star"] = float(J_star)
            fit["in_window"] = bool(f_low <= J_star <= f_high)

    # Argmax fallback (the v1 criterion).
    idx = int(np.argmax(gaps))
    argmax = {"J_mem": float(Js[idx]), "gap": float(gaps[idx]),
                "in_window": bool(f_low <= Js[idx] <= f_high)}

    # Structural comparator: gap(0.5) - gap(1.0) at >= 2 sigma_diff implies
    # partial SWAP beats full SWAP (the architectural claim).
    cmp_test = None
    j50 = next((d for d in sweep if abs(d["J_mem"] - 0.5) < 1e-6), None)
    j100 = next((d for d in sweep if abs(d["J_mem"] - 1.0) < 1e-6), None)
    if j50 and j100:
        diff = j50["gap"] - j100["gap"]
        diff_sem = math.sqrt(j50.get("gap_sem", 0.0)**2
                              + j100.get("gap_sem", 0.0)**2)
        sigma = diff / diff_sem if diff_sem > 0 else float("inf")
        cmp_test = {"diff": float(diff), "diff_sem": float(diff_sem),
                     "sigma": float(sigma),
                     "partial_beats_full": bool(diff > 0 and sigma >= 2.0)}
    return {"parabola_fit": fit, "argmax": argmax,
             "partial_vs_full": cmp_test,
             "pass_strict_parabola": fit["in_window"],
             "pass_lenient_argmax": argmax["in_window"]}


# ---------------------------------------------------------------------------
# THRESHOLDS (identical to v1 / Willow repo, locked at pre-registration)
# ---------------------------------------------------------------------------
THRESHOLDS = {
    "S_mean_low":      0.30,
    "S_mean_high":     0.65,
    "R_gap_min":       0.08,
    "R_sigma_min":     2.0,
    "T_null_tol":      0.03,
    "F_peak_low":      0.30,
    "F_peak_high":     0.70,
    "P_chirality_tol": 0.03,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=list(IBM_NOISE_PROFILES.keys()),
                     default="heron")
    ap.add_argument("--shots-total", type=int, default=10240,
                     help="single-run total shots per cell (replaces n_trials*shots)")
    ap.add_argument("--n-compute", type=int, default=1)
    ap.add_argument("--J-intra", type=float, default=0.1)
    ap.add_argument("--J-mem", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=None,
                     help="RNG seed for cirq + numpy (default: random)")
    ap.add_argument("--skip-F-sweep", action="store_true")
    ap.add_argument("--fine-sweep", action="store_true",
                     help="add J in {0.40, 0.45, 0.55, 0.60} to the F sweep")
    ap.add_argument("--p1q", type=float, default=None,
                     help="override single-qubit depolarising rate")
    ap.add_argument("--p2q", type=float, default=None,
                     help="override two-qubit depolarising rate")
    ap.add_argument("--p-meas", type=float, default=None,
                     help="override measurement bit-flip rate")
    args = ap.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    profile = IBM_NOISE_PROFILES[args.backend]
    p1q = args.p1q if args.p1q is not None else profile["p1q"]
    p2q = args.p2q if args.p2q is not None else profile["p2q"]
    p_meas = args.p_meas if args.p_meas is not None else profile["p_meas"]

    print(f"\nOBSERVABLE 22 v2 -- Pentachoric Verification Protocol")
    print(f"  backend:     {profile['label']}")
    print(f"  p1q/p2q/pM:  {p1q} / {p2q} / {p_meas}")
    print(f"  shots_total: {args.shots_total}")
    print(f"  J_intra={args.J_intra}, J_mem={args.J_mem}, seed={args.seed}")
    print()

    # -- Stage S ------------------------------------------------------------
    s_raw, s_raw_sem, s_mean, s_mean_sem = stage_S_substrate(
        args.n_compute, args.J_intra, p1q, p2q, p_meas, args.shots_total,
        seed=args.seed)
    s_pass = THRESHOLDS["S_mean_low"] <= s_mean <= THRESHOLDS["S_mean_high"]
    print(f"      22-S: {'PASS' if s_pass else 'FAIL'}\n")

    # -- Stage R ------------------------------------------------------------
    print(f"  [R] rotation: 3x3 write-read at J_mem={args.J_mem}")
    r_mat, r_sem = stage_R_3x3(
        args.n_compute, args.J_intra, args.J_mem, p1q, p2q, p_meas,
        args.shots_total, apply_tunnel=True, readout="v_D", seed=args.seed)
    r_cyc, r_off, r_gap, r_gap_sem, r_sigma = cycled_gap(r_mat, r_sem)
    print(f"      cycled = {r_cyc:.4f}   off = {r_off:.4f}")
    print(f"      cycled gap = {r_gap:+.4f} +/- {r_gap_sem:.4f}  ({r_sigma:+.2f} sigma)")
    r_pass = (r_gap >= THRESHOLDS["R_gap_min"]
               and r_sigma >= THRESHOLDS["R_sigma_min"])
    print(f"      22-R: {'PASS' if r_pass else 'FAIL'}\n")

    # -- Stage T ------------------------------------------------------------
    print(f"  [T] transfer null: no memory tunnel")
    t_mat, t_sem = stage_R_3x3(
        args.n_compute, args.J_intra, args.J_mem, p1q, p2q, p_meas,
        args.shots_total, apply_tunnel=False, readout="v_D", seed=args.seed)
    _, _, t_gap, t_gap_sem, _ = cycled_gap(t_mat, t_sem)
    print(f"      cycled gap (no tunnel) = {t_gap:+.4f} +/- {t_gap_sem:.4f}")
    t_pass = abs(t_gap) <= THRESHOLDS["T_null_tol"]
    print(f"      22-T: {'PASS' if t_pass else 'FAIL'}\n")

    # -- Stage F ------------------------------------------------------------
    f_summary = None
    if args.skip_F_sweep:
        print(f"  [F] frequency sweep: SKIPPED")
        f_pass = None
    else:
        Js = [0.0, 0.25, 0.5, 0.75, 1.0]
        if args.fine_sweep:
            Js = sorted(set(Js + [0.40, 0.45, 0.55, 0.60]))
        print(f"  [F] frequency: sweep J_mem in {Js}")
        sweep = []
        for J in Js:
            mat, sem = stage_R_3x3(
                args.n_compute, args.J_intra, J, p1q, p2q, p_meas,
                args.shots_total, apply_tunnel=True, readout="v_D",
                seed=args.seed)
            _, _, gap, gap_sem, _ = cycled_gap(mat, sem)
            sweep.append({"J_mem": J, "gap": gap, "gap_sem": gap_sem})
            print(f"      J_mem={J:.2f}  gap={gap:+.4f} +/- {gap_sem:.4f}")
        f_summary = f_gate_evaluate(
            sweep, THRESHOLDS["F_peak_low"], THRESHOLDS["F_peak_high"])
        ps = f_summary["parabola_fit"]
        am = f_summary["argmax"]
        cmp = f_summary["partial_vs_full"]
        if ps["J_star"] is not None:
            print(f"      parabola peak J*={ps['J_star']:.3f}  in window? "
                  f"{ps['in_window']}")
        else:
            print(f"      parabola fit non-concave; no peak (a={ps['a']})")
        print(f"      argmax J={am['J_mem']:.2f} gap={am['gap']:+.4f}  "
              f"in window? {am['in_window']}")
        if cmp:
            print(f"      gap(0.5) - gap(1.0) = {cmp['diff']:+.4f} "
                  f"+/- {cmp['diff_sem']:.4f}  ({cmp['sigma']:+.2f} sigma)")
            print(f"      partial-beats-full at >=2 sigma? "
                  f"{cmp['partial_beats_full']}")
        # Strict pass: parabola fit places vertex in window.
        f_pass = bool(f_summary["pass_strict_parabola"])
        print(f"      22-F (strict parabola): {'PASS' if f_pass else 'FAIL'}")
        if cmp and cmp["partial_beats_full"]:
            print(f"      22-F (structural cmp):    PASS  (partial > full)")
        elif cmp:
            print(f"      22-F (structural cmp):    FAIL  (partial <= full)")
        print()

    # -- Stage P ------------------------------------------------------------
    print(f"  [P] phase: read u_D directly")
    p_mat, p_sem = stage_R_3x3(
        args.n_compute, args.J_intra, args.J_mem, p1q, p2q, p_meas,
        args.shots_total, apply_tunnel=True, readout="u_D", seed=args.seed)
    p_diag, p_off, p_gap, p_gap_sem = diag_off_gap(p_mat, p_sem)
    print(f"      u_D diag={p_diag:.4f}  off={p_off:.4f}  gap={p_gap:+.4f} "
          f"+/- {p_gap_sem:.4f}")
    p_pass = abs(p_gap) <= THRESHOLDS["P_chirality_tol"]
    print(f"      22-P: {'PASS' if p_pass else 'FAIL'}\n")

    # -- Verdict ------------------------------------------------------------
    passes = {"S": s_pass, "R": r_pass, "T": t_pass,
                "F": f_pass, "P": p_pass}
    if all(p is True for p in passes.values()):
        verdict = "STRONG PASS (all five gates)"
    elif all(p is True for p in (s_pass, r_pass, p_pass)):
        verdict = "WEAK PASS (S+R+P confirmed; T or F degraded or skipped)"
    else:
        failed = [k for k, v in passes.items() if v is False]
        verdict = f"NULL (failed gates: {', '.join(failed)})"
    print(f"  PENTACHORIC VERDICT ({args.backend}): {verdict}")

    # -- Save JSON ----------------------------------------------------------
    outdir = Path(__file__).parent / "outputs"
    outdir.mkdir(exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    fname = outdir / f"obs22_pentachoric_ibm_v2_{args.backend}_{stamp}.json"
    payload = {
        "observable":   "obs22_pentachoric_ibm_v2",
        "backend":      profile["label"],
        "noise_model": {"p1q": p1q, "p2q": p2q, "p_meas": p_meas},
        "parameters":   vars(args),
        "thresholds":   THRESHOLDS,
        "measurement": {
            "S_raw":    s_raw, "S_raw_sem": s_raw_sem,
            "S_mean":   s_mean, "S_mean_sem": s_mean_sem, "S_pass": s_pass,
            "R_matrix":  r_mat.tolist(),     "R_matrix_sem":  r_sem.tolist(),
            "R_cycled":  r_cyc, "R_off":      r_off,
            "R_gap":     r_gap, "R_gap_sem":  r_gap_sem,
            "R_sigma":   r_sigma, "R_pass":   r_pass,
            "T_matrix":  t_mat.tolist(),     "T_matrix_sem":  t_sem.tolist(),
            "T_gap":     t_gap, "T_gap_sem":  t_gap_sem, "T_pass": t_pass,
            "F_summary": f_summary,
            "F_pass_strict": f_pass,
            "P_matrix":  p_mat.tolist(),     "P_matrix_sem":  p_sem.tolist(),
            "P_diag":    p_diag, "P_off":     p_off,
            "P_gap":     p_gap, "P_gap_sem":  p_gap_sem, "P_pass": p_pass,
        },
        "verdict":      verdict,
        "timestamp":    stamp,
    }
    fname.write_text(json.dumps(payload, indent=2))
    print(f"\n  Wrote {fname}")


if __name__ == "__main__":
    main()
