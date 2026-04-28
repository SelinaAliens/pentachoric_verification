#!/usr/bin/env python3
"""High-precision plateau ceiling extraction and closed-form constant search.

Goal: bypass SWAP-test shot sampling. Compute the cycled-gap exactly from
the state vector (no shot noise) at machine precision (~15 digits).
Then sweep J_mem on a fine grid, locate the plateau ceiling to high
precision, and try to match it to a closed form (mpmath.identify + custom
search over E6 / PSL(2,7) / Eisenstein-related integer combinations).

If a clean algebraic match exists, we have an architectural value.
If not, the plateau ceiling is genuinely transcendental and Option B
gives a clean negative result.

Method
------
1. Build the 19-qubit circuit through compute + memory tunnel (no SWAP test).
2. cirq state-vector simulation at complex128 precision.
3. Reduce to v_D's 2-qubit density matrix via partial trace.
4. Compute <Y|rho_vD|Y> for each Z_3 label Y; this equals (P(swap=0)*2 - 1),
   so sqrt() gives the SWAP-test overlap.
5. Build 3x3 matrix exactly. Compute cycled-mean, off-mean, gap.
6. Sweep J_mem with 0.001 resolution near the plateau peak. Find max gap.
7. Closed-form search: mpmath.identify + custom integer-ratio scan.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import cirq
import mpmath

sys.path.insert(0, str(Path(r"C:\Users\selin\tesseract_quantum_implementation\cirq")))

from run_p4s_tesseract_memory_cirq import (
    build_write_read_circuit, LABELS, LABEL_IDX,
    U_A, V_A, U_B, V_B, U_C, V_C, U_D, V_D, REF, ANCILLA,
)
from run_p4s_Z3_three_cirq import z3_eigenstate
from run_p4s_Z3_cirq import state_prep_2q
from run_p4s_cirq import T_CYCLE
import importlib

# We need a no-SWAP circuit. Build it by reusing the same primitives
# directly.
from run_p4s_tesseract_memory_cirq import (
    compute_triangle_step, cross_chiral_tunnel,
)


def build_compute_plus_memory(label_X, n_compute, J_intra, J_mem,
                                apply_memory_tunnel=True):
    """Same as build_write_read_circuit but stops before reference prep
    and SWAP test. Returns a 16-qubit circuit (q0..q15) and the full
    qubit list for explicit ordering."""
    qubits = cirq.LineQubit.range(16)  # only 16 qubits needed (no ref/anc)
    q_uA = [qubits[i] for i in U_A]; q_vA = [qubits[i] for i in V_A]
    q_uB = [qubits[i] for i in U_B]; q_vB = [qubits[i] for i in V_B]
    q_uC = [qubits[i] for i in U_C]; q_vC = [qubits[i] for i in V_C]
    q_uD = [qubits[i] for i in U_D]; q_vD = [qubits[i] for i in V_D]

    qc = cirq.Circuit()
    # Touch all 16 qubits with identity so cirq simulates the full Hilbert
    # space (otherwise it auto-reduces to active qubits and ordering breaks).
    for q in qubits:
        qc.append(cirq.I(q))
    lx = z3_eigenstate(LABEL_IDX[label_X])
    qc.append(state_prep_2q(lx, "uA").on(*q_uA))
    qc.append(state_prep_2q(lx, "vA").on(*q_vA))
    qc.append(state_prep_2q(lx, "uB").on(*q_uB))
    qc.append(state_prep_2q(lx, "vB").on(*q_vB))
    qc.append(state_prep_2q(lx, "uC").on(*q_uC))
    qc.append(state_prep_2q(lx, "vC").on(*q_vC))

    for s in range(n_compute * T_CYCLE):
        qc.append(compute_triangle_step(
            q_uA, q_vA, q_uB, q_vB, q_uC, q_vC, s, J_intra))

    if apply_memory_tunnel:
        qc.append(cross_chiral_tunnel(q_uC, q_vD, J_mem))

    return qc, q_vD, qubits


# Cycled cells: (alpha, gamma), (beta, alpha), (gamma, beta)
CYCLED_IDX = [(0, 2), (1, 0), (2, 1)]


def exact_cycled_gap(J_mem, J_intra=0.1, n_compute=1):
    """Compute cycled-gap at machine precision (no shot noise)."""
    sim = cirq.Simulator(dtype=np.complex128)
    matrix = np.zeros((3, 3))
    for i, X in enumerate(LABELS):
        qc, q_vD, qubits = build_compute_plus_memory(X, n_compute, J_intra, J_mem)
        result = sim.simulate(qc, qubit_order=qubits)
        psi = result.final_state_vector
        # Reduce to v_D's 2-qubit density matrix at indices V_D = [14, 15]
        rho_vD = cirq.density_matrix_from_state_vector(
            psi, indices=[V_D[0], V_D[1]])
        for j, Y in enumerate(LABELS):
            yvec = z3_eigenstate(LABEL_IDX[Y])  # (4,) complex
            overlap_sq = float(np.real(yvec.conj() @ rho_vD @ yvec))
            overlap_sq = max(0.0, overlap_sq)
            matrix[i, j] = np.sqrt(overlap_sq)
    cycled = np.array([matrix[i, j] for i, j in CYCLED_IDX])
    mask = np.ones((3, 3), dtype=bool)
    for i, j in CYCLED_IDX:
        mask[i, j] = False
    off = matrix[mask]
    return float(cycled.mean() - off.mean()), matrix


def find_plateau_peak():
    """Scan J_mem near the predicted peak, find maximum gap."""
    # First coarse pass to bracket
    print("=== Coarse J_mem scan (resolution 0.01) ===")
    Js_coarse = np.arange(0.55, 0.85, 0.01)
    gaps_coarse = []
    for J in Js_coarse:
        g, _ = exact_cycled_gap(float(J))
        gaps_coarse.append(g)
        print(f"  J={J:.3f}  gap={g:.10f}")
    best_J = Js_coarse[int(np.argmax(gaps_coarse))]
    print(f"  Coarse argmax: J={best_J:.3f}")

    # Fine pass at resolution 0.001
    print("\n=== Fine J_mem scan around peak (resolution 0.001) ===")
    Js_fine = np.arange(best_J - 0.02, best_J + 0.02, 0.001)
    gaps_fine = []
    for J in Js_fine:
        g, _ = exact_cycled_gap(float(J))
        gaps_fine.append(g)
        if abs(J - best_J) < 0.005:
            print(f"  J={J:.4f}  gap={g:.12f}")
    best_idx = int(np.argmax(gaps_fine))
    best_J_fine = Js_fine[best_idx]
    best_gap = gaps_fine[best_idx]
    print(f"  Fine argmax: J={best_J_fine:.4f}, gap={best_gap:.12f}")

    # Parabolic refinement using 5 nearest points
    lo = max(0, best_idx - 2)
    hi = min(len(Js_fine), best_idx + 3)
    Js5 = Js_fine[lo:hi]
    gs5 = gaps_fine[lo:hi]
    a, b, c = np.polyfit(Js5, gs5, 2)
    if a < 0:
        J_star = -b / (2 * a)
        gap_star = a * J_star**2 + b * J_star + c
        print(f"  Parabola vertex: J* = {J_star:.6f}, "
                f"gap* = {gap_star:.12f}")
        return float(gap_star), float(J_star)
    return float(best_gap), float(best_J_fine)


def closed_form_search(target, name="value"):
    """Try mpmath.identify and a custom search over Eisenstein/E6 integer
    combinations."""
    print(f"\n=== Closed-form search for {name} = {target:.15f} ===")

    # mpmath.identify with relevant constants
    mpmath.mp.dps = 30
    candidates = []
    try:
        constants = [mpmath.pi, mpmath.e, mpmath.sqrt(2), mpmath.sqrt(3),
                     mpmath.sqrt(5), mpmath.sqrt(7), mpmath.phi,
                     mpmath.log(2), mpmath.log(3), mpmath.zeta(2),
                     mpmath.zeta(3)]
        names = ['pi', 'e', 'sqrt(2)', 'sqrt(3)', 'sqrt(5)', 'sqrt(7)',
                 'phi', 'log(2)', 'log(3)', 'zeta(2)', 'zeta(3)']
        result = mpmath.identify(target, constants, tol=1e-10)
        if result is not None:
            print(f"  mpmath.identify: {result}")
            candidates.append(("mpmath", result))
    except Exception as e:
        print(f"  mpmath.identify failed: {e}")

    # Custom: search over rationals m/n with m, n drawn from architectural
    # integer pool: {1, 2, 3, 4, 5, 6, 7, 12, 13, 24, 28, 31, 36, 42, 62, 75,
    # 78, 137, 144, 168}. Tolerance 1e-9.
    pool = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 24, 28, 31, 36, 42,
              47, 62, 72, 75, 78, 109, 137, 144, 168]
    print(f"  Searching m/n with m,n in {{1..12, architectural integers}}...")
    matches = []
    for m in pool:
        for n in pool:
            if n == 0:
                continue
            val = m / n
            if abs(val - target) < 1e-9:
                matches.append((m, n, val))
    matches.sort(key=lambda x: abs(x[2] - target))
    if matches:
        print(f"  Best simple-rational matches:")
        for m, n, val in matches[:5]:
            print(f"    {m}/{n} = {val:.15f}  (delta = {val - target:+.2e})")
    else:
        print("  No simple m/n match within 1e-9.")

    # Search over m/(n*pi), m*pi/n, m*sqrt(k)/n
    print(f"  Searching m/(n*pi), m*pi/n, m*sqrt(k)/n...")
    pi_matches = []
    for m in pool:
        for n in pool:
            if n == 0:
                continue
            for f, fname in [(np.pi, 'pi'), (np.e, 'e'),
                              (np.sqrt(2), 'sqrt2'),
                              (np.sqrt(3), 'sqrt3')]:
                for sign in [+1, -1]:
                    v1 = sign * m / (n * f)
                    v2 = sign * m * f / n
                    if abs(v1 - target) < 1e-9:
                        pi_matches.append((f"{sign:+d}*{m}/({n}*{fname})", v1))
                    if abs(v2 - target) < 1e-9:
                        pi_matches.append((f"{sign:+d}*{m}*{fname}/{n}", v2))
    pi_matches.sort(key=lambda x: abs(x[1] - target))
    if pi_matches:
        print(f"  Best {len(pi_matches)} matches (constant-scaled rationals):")
        for expr, val in pi_matches[:5]:
            print(f"    {expr} = {val:.15f}  (delta = {val - target:+.2e})")
    else:
        print("  No constant-scaled rational match within 1e-9.")

    # Search over differences/combinations of specific E6/PSL(2,7) ratios
    print(f"  Searching combinations of {{4/3, 3/2, 1/6, 1/3, 1/12, 5/42, ...}}...")
    arch_constants = {
        '4/3': 4/3, '3/2': 3/2, '1/6': 1/6, '1/3': 1/3, '1/12': 1/12,
        '5/42': 5/42, '3/13': 3/13, '47/144': 47/144,
        '28/29': 28/29, '2/3': 2/3, '1/4': 1/4, 'sqrt(3)/10': np.sqrt(3)/10,
        '17/100': 0.17, 'sqrt(3)/(2*pi)': np.sqrt(3)/(2*np.pi),
        '1/(2*pi)': 1/(2*np.pi), 'pi/18': np.pi/18,
    }
    arch_matches = []
    for n1, v1 in arch_constants.items():
        for n2, v2 in arch_constants.items():
            for op, opname in [(v1+v2, '+'), (v1-v2, '-'),
                                (v1*v2, '*'), (v1/v2 if v2 else 0, '/')]:
                if op == 0:
                    continue
                if abs(op - target) < 1e-7:
                    arch_matches.append((f"({n1}){opname}({n2})", op))
    arch_matches.sort(key=lambda x: abs(x[1] - target))
    if arch_matches:
        print(f"  Architectural constant combinations within 1e-7:")
        for expr, val in arch_matches[:10]:
            print(f"    {expr} = {val:.15f}  (delta = {val - target:+.2e})")
    else:
        print("  No architectural-constant combination match within 1e-7.")

    return candidates


def main():
    np.set_printoptions(precision=12, suppress=False)

    print("=" * 70)
    print("OPTION B: Exact plateau ceiling extraction + closed-form search")
    print("=" * 70)
    print(f"Method: state-vector simulation at complex128, partial trace,")
    print(f"        analytic SWAP-test overlap. ~15 digits of precision.")
    print()

    # 1. Verify reproducibility against the empirical 0.170 from earlier runs
    g_05, mat = exact_cycled_gap(0.5)
    print(f"Sanity check: J_mem=0.5 cycled-gap = {g_05:.10f}")
    print(f"  (empirical 200k-shot run gave 0.16289 +/- 0.00130)")
    print()

    # 2. Find plateau peak to high precision
    peak_gap, peak_J = find_plateau_peak()
    print(f"\nPLATEAU PEAK (exact):")
    print(f"  J* = {peak_J:.6f}")
    print(f"  gap* = {peak_gap:.15f}")

    # 3. Closed-form search at the peak
    closed_form_search(peak_gap, name="plateau peak gap")

    # 4. Also search at a few specific J values to look for clean rationals
    print()
    for J in [0.5, 0.6, 0.65, 0.7, 0.75, 1.0]:
        g, _ = exact_cycled_gap(J)
        print(f"\n--- J_mem = {J:.2f}, gap = {g:.15f} ---")
        closed_form_search(g, name=f"gap at J={J}")


if __name__ == "__main__":
    main()
