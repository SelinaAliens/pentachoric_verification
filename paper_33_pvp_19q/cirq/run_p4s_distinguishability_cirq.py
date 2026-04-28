#!/usr/bin/env python3
"""
Protocol 4S-Distinguishability -- Test B of Paper 35 Observable 21.

Tests whether the three-layer stack DISCRIMINATES between different stored
labels at readout. Rather than measuring absolute fidelity to a fixed
reference, this test computes the 3x3 cross-fidelity matrix:

    F[write_X, ref_Y] = |<ref_Y | output_env>|

for each X, Y in {alpha, beta, gamma} and each output register in
{u_env, v_env}.

Recognition works if the DIAGONAL (X == Y) dominates the OFF-DIAGONAL:

    RECOGNITION_GAP = mean(diagonal) - mean(off-diagonal) > 0 at >= 3 sigma

For the BOUNDARY readout (v_env), the merkabit architecture predicts
a sharper sub-pattern rooted in chirality:

    alpha (self-dual)        -> v_env matches alpha strongest (on diag)
    beta  (forward chirality)-> v_env matches GAMMA strongest (time-reversed)
    gamma (inverse chirality)-> v_env matches BETA  strongest (time-reversed)

i.e. the v_env readout for beta/gamma writes should be maximised by the
CONJUGATE reference, not the same-label reference. This is the u/v
bifurcation signature: v is the time-reversed partner of u, so reading
v against the conjugate of the written u gives the true recognition
match. alpha is self-dual and so matches itself.

Falsifier: if all nine cells of the v_env matrix are statistically
identical, the boundary readout carries no label information -- either
the envelope dynamics thermalise too fast, or the u-capture did not
happen.

Usage:
  python run_p4s_distinguishability_cirq.py
  python run_p4s_distinguishability_cirq.py --n-trials 5 --n-envelope 1
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

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from run_p4s_compute_store_cirq import (
    build_circuit,  # 22-qubit builder: (label_A, label_B, label_C, n_c, n_e,
                    #                     J_intra, J_inter, L1, L2, apply_inter,
                    #                     readout, seeds) -> circuit
)
from run_p4s_cirq import overlap_from_swap

RESULTS_DIR = SCRIPT_DIR.parent / "results"

LABELS = ['alpha', 'beta', 'gamma']


def build_cross_circuit(write_label, ref_label, n_compute, n_envelope,
                         J_intra, J_inter, cross_L1, cross_L2,
                         readout, env_u_seed, env_v_seed,
                         p_sign=+1):
    """Build a compute+store circuit writing `write_label` to the
    triangle (all three sites carry the same label, driving an
    unambiguous compute-cell output), then reading the target envelope
    register against a reference prepared in `ref_label`.

    To get a proper cross-fidelity test, we need the reference in the
    SWAP test to be ref_label, not the written label. Since the existing
    build_circuit uses label_C for the reference, we build a custom
    circuit here that separates 'what we write' from 'what we read'.
    """
    # Local triangle step that supports p_sign chirality flip.
    import cirq
    import numpy as np
    from run_p4s_compute_store_cirq import (
        U_A, V_A, U_B, V_B, U_C, V_C, U_ENV, V_ENV, REF, ANCILLA,
        envelope_step, inter_layer_write,
        three_qubit_swap_test, lift_4_to_8,
        T_CYCLE, OCTO_T_CYCLE,
    )
    from run_p4s_Z3_three_cirq import z3_eigenstate
    from run_p4s_Z3_cirq import state_prep_2q
    from run_p4s_octonion_cirq import state_prep_ops as octo_state_prep_ops
    from run_p4s_cirq import cross_gate_4, horizontal_gate_4, diagonal_gate_4
    from run_p4s_Z3_three_P_cirq import internal_step_angles_chiral, p_gate_4

    def compute_merkabit_internal(q_u, q_v, step_index, p_sign):
        th_c, th_h, th_d, phi_p = internal_step_angles_chiral(
            step_index % T_CYCLE)
        # Chirality flip: negate phi_p to swap Pf <-> Pi
        Pf, Pi = p_gate_4(p_sign * phi_p)
        yield cirq.MatrixGate(Pf, qid_shape=(2, 2)).on(*q_u)
        yield cirq.MatrixGate(Pi, qid_shape=(2, 2)).on(*q_v)
        for gate_fn, theta in [(cross_gate_4, th_c),
                                (horizontal_gate_4, th_h),
                                (diagonal_gate_4, th_d)]:
            Uf, Ui = gate_fn(theta)
            yield cirq.MatrixGate(Uf, qid_shape=(2, 2)).on(*q_u)
            yield cirq.MatrixGate(Ui, qid_shape=(2, 2)).on(*q_v)

    def cross_chiral_tunnel_2q(q_uX, q_vY, J):
        for i in range(2):
            yield (cirq.ISWAP ** J).on(q_uX[i], q_vY[i])

    def triangle_step_with_chirality(q_uA, q_vA, q_uB, q_vB,
                                      q_uC, q_vC, step_index, J_intra, p_sign):
        yield from compute_merkabit_internal(q_uA, q_vA, step_index, p_sign)
        yield from compute_merkabit_internal(q_uB, q_vB, step_index, p_sign)
        yield from compute_merkabit_internal(q_uC, q_vC, step_index, p_sign)
        if J_intra > 0:
            yield from cross_chiral_tunnel_2q(q_uA, q_vB, J_intra)
            yield from cross_chiral_tunnel_2q(q_uB, q_vC, J_intra)
            yield from cross_chiral_tunnel_2q(q_uC, q_vA, J_intra)

    qubits = cirq.LineQubit.range(22)
    q_uA = [qubits[i] for i in U_A]; q_vA = [qubits[i] for i in V_A]
    q_uB = [qubits[i] for i in U_B]; q_vB = [qubits[i] for i in V_B]
    q_uC = [qubits[i] for i in U_C]; q_vC = [qubits[i] for i in V_C]
    q_ue = [qubits[i] for i in U_ENV]; q_ve = [qubits[i] for i in V_ENV]
    q_ref = [qubits[i] for i in REF]
    anc = qubits[ANCILLA]

    qc = cirq.Circuit()
    lab_map = {'alpha': 0, 'beta': 1, 'gamma': 2}
    # All three compute sites carry write_label (uniform input)
    w = z3_eigenstate(lab_map[write_label])
    qc.append(state_prep_2q(w, "uA").on(*q_uA))
    qc.append(state_prep_2q(w, "vA").on(*q_vA))
    qc.append(state_prep_2q(w, "uB").on(*q_uB))
    qc.append(state_prep_2q(w, "vB").on(*q_vB))
    qc.append(state_prep_2q(w, "uC").on(*q_uC))
    qc.append(state_prep_2q(w, "vC").on(*q_vC))

    rng_u = np.random.default_rng(env_u_seed)
    rng_v = np.random.default_rng(env_v_seed)
    ue0 = rng_u.normal(size=8) + 1j * rng_u.normal(size=8)
    ve0 = rng_v.normal(size=8) + 1j * rng_v.normal(size=8)
    ue0 /= np.linalg.norm(ue0); ve0 /= np.linalg.norm(ve0)
    qc.append(octo_state_prep_ops(q_ue, ue0))
    qc.append(octo_state_prep_ops(q_ve, ve0))

    for s in range(n_compute * T_CYCLE):
        qc.append(triangle_step_with_chirality(q_uA, q_vA, q_uB, q_vB,
                                                 q_uC, q_vC, s, J_intra,
                                                 p_sign))

    qc.append(inter_layer_write(q_uC, q_ue, J_inter))

    for s in range(n_envelope * OCTO_T_CYCLE):
        qc.append(envelope_step(q_ue, q_ve, s, cross_L1, cross_L2))

    # REFERENCE: prepared in ref_label (NOT write_label). This is the key
    # to the cross-fidelity test.
    r = z3_eigenstate(lab_map[ref_label])
    qc.append(octo_state_prep_ops(q_ref, lift_4_to_8(r)))

    tgt = q_ue if readout == 'u_env' else q_ve
    qc.append(three_qubit_swap_test(anc, q_ref, tgt))
    qc.append(cirq.measure(anc, key='anc'))
    return qc


def run_distinguishability(n_compute, n_envelope, J_intra, J_inter,
                            cross_L1, cross_L2, shots, n_trials, p_sign=+1):
    """Run the 3x3 cross-fidelity matrix for u_env and v_env readouts."""
    sim = cirq.Simulator()
    results = {'u_env': {w: {r: [] for r in LABELS} for w in LABELS},
               'v_env': {w: {r: [] for r in LABELS} for w in LABELS}}
    total_circuits = len(LABELS) ** 2 * 2 * n_trials
    print(f"Building and running {total_circuits} circuits "
          f"(p_sign={p_sign:+d}, {n_trials} trials x 9 (write x ref) x 2 readouts)...")
    print()
    c = 0
    for write in LABELS:
        for ref in LABELS:
            for readout in ['u_env', 'v_env']:
                for t in range(n_trials):
                    c += 1
                    qc = build_cross_circuit(write, ref,
                                              n_compute, n_envelope,
                                              J_intra, J_inter,
                                              cross_L1, cross_L2,
                                              readout,
                                              env_u_seed=10 * t,
                                              env_v_seed=10 * t + 1,
                                              p_sign=p_sign)
                    r = sim.run(qc, repetitions=shots)
                    zeros = int(r.histogram(key='anc').get(0, 0))
                    results[readout][write][ref].append(
                        overlap_from_swap(zeros, shots))
            print(f"  write={write} ref={ref}  [{c}/{total_circuits}]")
    return results


def summarise(results, readout):
    """Compute and print 3x3 mean fidelity matrix + diagonal vs off-diag gap."""
    print(f"\n=== {readout} cross-fidelity matrix (mean +/- SEM) ===")
    # Header
    print(f"{'':>10}  " + "  ".join(f"{r:>16s}" for r in LABELS))
    matrix = np.zeros((3, 3))
    matrix_sem = np.zeros((3, 3))
    for i, w in enumerate(LABELS):
        row = []
        for j, r in enumerate(LABELS):
            arr = np.array(results[readout][w][r])
            m = float(arr.mean())
            s = float(arr.std(ddof=1) / math.sqrt(len(arr)))
            matrix[i, j] = m; matrix_sem[i, j] = s
            row.append(f"{m:.3f}+/-{s:.3f}")
        print(f"  write={w:>5s} | " + "  ".join(f"{c:>16s}" for c in row))

    # Diagonal vs off-diagonal
    diag = np.array([matrix[i, i] for i in range(3)])
    off  = np.array([matrix[i, j] for i in range(3) for j in range(3) if i != j])
    diag_mean, diag_sem = float(diag.mean()), float(diag.std(ddof=1) / math.sqrt(3))
    off_mean, off_sem   = float(off.mean()),  float(off.std(ddof=1) / math.sqrt(6))
    gap = diag_mean - off_mean
    gap_sem = math.sqrt(diag_sem ** 2 + off_sem ** 2)
    sigma = gap / gap_sem if gap_sem > 0 else float('inf')
    print(f"  diagonal     = {diag_mean:.4f} +/- {diag_sem:.4f}")
    print(f"  off-diagonal = {off_mean:.4f} +/- {off_sem:.4f}")
    print(f"  gap (diag - off) = {gap:+.4f} +/- {gap_sem:.4f}  ({sigma:+.1f} sigma)")

    # Chirality-correct cells are the key prediction for v_env:
    #   alpha -> alpha     (self-dual stays same)
    #   beta  -> gamma     (forward chirality read by time-reversed partner)
    #   gamma -> beta      (inverse chirality read by time-reversed partner)
    chirality_correct_idx = [(0, 0), (1, 2), (2, 1)]
    chirality_wrong_idx = [(i, j) for i in range(3) for j in range(3)
                            if (i, j) not in chirality_correct_idx]
    cc = np.array([matrix[i, j] for (i, j) in chirality_correct_idx])
    cw = np.array([matrix[i, j] for (i, j) in chirality_wrong_idx])
    cc_mean = float(cc.mean()); cc_sem = float(cc.std(ddof=1) / math.sqrt(3))
    cw_mean = float(cw.mean()); cw_sem = float(cw.std(ddof=1) / math.sqrt(6))
    chir_gap = cc_mean - cw_mean
    chir_gap_sem = math.sqrt(cc_sem ** 2 + cw_sem ** 2)
    chir_sigma = chir_gap / chir_gap_sem if chir_gap_sem > 0 else float('inf')
    print(f"  chirality-correct {{a->a, b->g, g->b}} mean = {cc_mean:.4f} +/- {cc_sem:.4f}")
    print(f"  chirality-wrong (other 6 cells)     mean = {cw_mean:.4f} +/- {cw_sem:.4f}")
    print(f"  CHIRALITY GAP     = {chir_gap:+.4f} +/- {chir_gap_sem:.4f}  ({chir_sigma:+.1f} sigma)")

    # Per-cell chirality check for v_env
    chirality_pattern = None
    if readout == 'v_env':
        bg = matrix[1, 2]  # beta -> gamma
        bb = matrix[1, 1]  # beta -> beta
        gb = matrix[2, 1]  # gamma -> beta
        gg = matrix[2, 2]  # gamma -> gamma
        aa = matrix[0, 0]  # alpha -> alpha (self-dual)
        chirality_pattern = {
            'beta_write_gamma_ref_F':  float(bg),
            'beta_write_beta_ref_F':   float(bb),
            'beta_prefers_gamma':      bool(bg > bb),
            'beta_gamma_minus_beta_beta': float(bg - bb),
            'gamma_write_beta_ref_F':  float(gb),
            'gamma_write_gamma_ref_F': float(gg),
            'gamma_prefers_beta':      bool(gb > gg),
            'gamma_beta_minus_gamma_gamma': float(gb - gg),
            'alpha_diag_F':            float(aa),
        }
        print(f"  [beta  write] gamma-ref F={bg:.3f} vs beta-ref F={bb:.3f}  "
              f"{'MATCH (v reads conjugate)' if bg > bb else 'NO MATCH'}")
        print(f"  [gamma write] beta-ref F={gb:.3f} vs gamma-ref F={gg:.3f}  "
              f"{'MATCH (v reads conjugate)' if gb > gg else 'NO MATCH'}")
        print(f"  [alpha write] alpha-ref F={aa:.3f}  (self-dual)")

    return {
        'matrix':         matrix.tolist(),
        'matrix_sem':     matrix_sem.tolist(),
        'diagonal_mean':  diag_mean,
        'diagonal_sem':   diag_sem,
        'off_mean':       off_mean,
        'off_sem':        off_sem,
        'diag_off_gap':   gap,
        'diag_off_sigma': sigma,
        'chirality_correct_mean': cc_mean,
        'chirality_correct_sem':  cc_sem,
        'chirality_wrong_mean':   cw_mean,
        'chirality_wrong_sem':    cw_sem,
        'chirality_gap':          chir_gap,
        'chirality_sigma':        chir_sigma,
        'chirality_pattern':      chirality_pattern,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n-compute',  type=int,   default=1)
    ap.add_argument('--n-envelope', type=int,   default=1)
    ap.add_argument('--J-intra',    type=float, default=0.1)
    ap.add_argument('--J-inter',    type=float, default=1.0)
    ap.add_argument('--cross-L1',   type=float, default=0.3)
    ap.add_argument('--cross-L2',   type=float, default=0.2)
    ap.add_argument('--shots',      type=int,   default=2048)
    ap.add_argument('--n-trials',   type=int,   default=5)
    ap.add_argument('--p-sign',     type=int,   default=+1,
                     choices=[+1, -1],
                     help='Chirality of the P gate: +1 forward (default), '
                          '-1 reversed. Test the symmetry-flip prediction: '
                          'reversed P should make the chirality-correct pattern '
                          'become {alpha->alpha, beta->beta, gamma->gamma} '
                          'diagonal (self-match) because the time arrow has '
                          'been reversed for the compute cell.')
    args = ap.parse_args()

    print("Protocol 4S-Distinguishability -- Test B of Paper 35 Observable 21")
    print(f"  22-qubit triangle compute + 1 octonion envelope")
    print(f"  n_compute={args.n_compute}, n_envelope={args.n_envelope}")
    print(f"  J_intra={args.J_intra}, J_inter={args.J_inter}")
    print(f"  shots={args.shots}, trials_per_cell={args.n_trials}")
    print()
    print("Writes uniform label across all three compute sites;")
    print("measures cross-fidelity 3x3 matrix of (write, reference) vs both")
    print("readout registers u_env (DIRECT) and v_env (BOUNDARY).")
    print()
    print("Predictions:")
    print("  u_env (DIRECT):    diagonal dominates (each write matches its")
    print("                     own reference best)")
    print("  v_env (BOUNDARY):  chirality pattern -- beta writes prefer gamma")
    print("                     reference, gamma writes prefer beta reference,")
    print("                     alpha writes prefer alpha (self-dual).")
    print()

    results = run_distinguishability(args.n_compute, args.n_envelope,
                                       args.J_intra, args.J_inter,
                                       args.cross_L1, args.cross_L2,
                                       args.shots, args.n_trials,
                                       p_sign=args.p_sign)

    print()
    print("=" * 78)
    summary_u = summarise(results, 'u_env')
    print()
    summary_v = summarise(results, 'v_env')
    print("=" * 78)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp":  datetime.now().isoformat(timespec="seconds"),
        "protocol":   "P4S-Distinguishability (22-qubit Test B)",
        "n_qubits":   22,
        "n_compute":  args.n_compute,
        "n_envelope": args.n_envelope,
        "J_intra":    args.J_intra,
        "J_inter":    args.J_inter,
        "cross_L1":   args.cross_L1,
        "cross_L2":   args.cross_L2,
        "shots":      args.shots,
        "n_trials":   args.n_trials,
        "raw":        {r: {w: {ref: results[r][w][ref] for ref in LABELS}
                            for w in LABELS} for r in ['u_env', 'v_env']},
        "summary_u_env": summary_u,
        "summary_v_env": summary_v,
    }
    out = RESULTS_DIR / f"p4s_distinguishability_{datetime.now():%Y%m%dT%H%M%S}.json"
    out.write_text(json.dumps(payload, indent=2))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
