# Pre-Registered Predictions: Pentachoric Verification Protocol (IBM Hardware)

**Date:** 21 April 2026 (initial deposit)
**Authors:** Selina Stenberg, Claude (Anthropic, Opus 4.7), Thor Henning Hetland (IBM track)
**Companion Zenodo references:** Paper 35 (forthcoming), Papers 31–34 (forthcoming), Papers 24–26 (DOI 10.5281/zenodo.19484743, 19502830, 19554030)
**Target hardware:** IBM Eagle r3 (`ibm_strasbourg`, `ibm_brussels`) and Heron r2 (`ibm_kingston`).
**Sibling repo:** `selinaserephina-star/pentachoric_verification_protocol` (Willow target) — identical thresholds, identical protocol.

## Claim being pre-registered

The merkabit architecture (Papers 31–35) is a **primitive-complete, self-hosting quantum computer**. Every operation required for computation — write, compute, communicate, store, retrieve, clock — reduces to native merkabit dynamics. No external gate library is needed.

This document pre-registers falsifiable pass/fail thresholds for four hardware observables on IBM Eagle r3 and Heron r2:

- **Observable 14** — cross-chiral tunnel (Paper 31, 9 qubits)
- **Observable 16** — triangle cellular automaton (Paper 32, 13 qubits)
- **Observable 17** — 4-square Z₃ loop-phase holonomy (Paper 32, 17 qubits)
- **Observable 22** — Pentachoric Verification Protocol (Paper 35, 19 qubits) — *the primary test*

The git SHA of the initial commit of this file is the timestamped pre-registration anchor. Thresholds below are baked into the Python submission scripts at `selinaserephina-star/tesseract_quantum_implementation/willow/` (commit `9d0c19b`).

---

## Observable 14 — Cross-chiral tunnel (Paper 31, 9 qubits)

**Circuit.** Two tesseract merkabits A, B (2 × 4 = 8 data qubits + 1 SWAP-test ancilla). Z₃ × Z₃ ordered-pair input families, Protocol 4S internal dynamics for n = 1 Coxeter period, cross-chiral iSWAP^J between u_A and v_B at J = 0.1 per step. SWAP test measures \|⟨u_A\|v_B⟩\|.

| Threshold | Value | Basis |
|---|---|---|
| 14a-S: directional gap (strong pass) | ≥ 0.40 | Cirq ideal at J=0.1, n=1 |
| 14a-W: directional gap (weak pass) | ≥ 0.30 | " |
| 14a-N: null | < 0.20 | " |
| 14a-D: (β, γ) destructive zero | ≤ 0.10 | " |
| 14a-C: (γ, β) constructive peak | ≥ 0.50 | " |
| 14b: noisy destructive persistence | ≤ 0.20 | Cirq at p_depol = 0.003 |

**Falsification:** Gap < 0.20 at 3σ falsifies the cross-chiral tunnel as a directional computational primitive.

**Script:** `tesseract_quantum_implementation/willow/obs14_tunnel.py`. Budget: ~25 QPU-min.

---

## Observable 16 — Triangle cellular automaton (Paper 32, 13 qubits)

**Circuit.** Three tesseract merkabits A, B, C in a closed triangle (12 data qubits + 1 ancilla). Cross-chiral tunnels on all three edges at J = 0.1. Triangle input families sweep the 9 ordered-pair Z₃ × Z₃ lookup-table entries.

| Threshold | Value | Basis |
|---|---|---|
| 16a-S: (β, γ) entry strong pass | ≤ 0.05 | Cirq ideal triangle |
| 16a-W: (β, γ) entry weak pass | ≤ 0.10 | " |
| 16a-N: null | > 0.15 | " |
| 16a-C: (γ, β) entry | ≥ 0.50 | " |
| 16b: triangle vs 4-square agreement | ≤ 0.03 | Paper 32 Section 3 topology invariance |

**Falsification:** (β, γ) > 0.15 at 3σ falsifies the destructive-zero prediction. Agreement > 0.03 between triangle and 4-square bond values falsifies topology-independence.

**Script:** `tesseract_quantum_implementation/willow/obs16_triangle.py`. Budget: ~15 QPU-min.

---

## Observable 17 — 4-square Z₃ loop-phase holonomy (Paper 32, 17 qubits)

**Circuit.** Four tesseract merkabits A, B, C, D on an oriented plaquette (16 data qubits + 1 ancilla). Perimeter tunnels u_A ↔ v_B, u_B ↔ v_C, u_C ↔ v_D, u_D ↔ v_A at J = 0.1. Eight Z₃ input families grouped by Z₃ loop-phase class (trivial / ω / ω²).

| Threshold | Value | Basis |
|---|---|---|
| 17a-S: mean between-class gap (strong) | ≥ 0.15 | Paper 32 Section 5 |
| 17a-W: mean between-class gap (weak) | ≥ 0.08 | " |
| 17a-B: separable bonds (of 4) | ≥ 3 | " |
| 17b: topology agreement (vs triangle) | ≤ 0.05 | Paper 32 Section 3 |
| 17c: separable cells at ≥ 3σ | ≥ 15 of 28 | Paper 33 capacity projection |
| 17d: diagonal path-residual | ≤ 0.10 | Information flows perimetrically |

**Falsification:** Fewer than 3 of 4 perimeter bonds separable by loop-phase class falsifies the Z₃-gauge-lattice interpretation.

**Script:** `tesseract_quantum_implementation/willow/obs17_square.py`. Budget: ~65 QPU-min.

---

## Observable 22 — The Pentachoric Verification Protocol (Paper 35, 19 qubits) — *primary test*

**Circuit.** Three tesseract merkabits A, B, C in a compute triangle (12 qubits) + database merkabit D (4 qubits) + reference register (2 qubits) + SWAP-test ancilla (1 qubit) = **19 qubits**. Five simulation stages; each isolates one of the five pentachoric gates of the ouroboros cycle.

### The five gates

| Gate | Name | Protocol | Pass threshold |
|---|---|---|---|
| **S** | Substrate | Compute triangle alone; measure ⟨u\|v⟩ on A, B, C at n = 1 Coxeter period | mean \|⟨u\|v⟩\| ∈ [0.30, 0.65] |
| **R** | Rotation | 3×3 write-read matrix at J_mem = 0.5; measure v_D vs Z₃ reference | cycled-diagonal gap ≥ +0.08 at σ ≥ 2.0 |
| **T** | Transfer (null) | Same as R, no memory tunnel applied | \|cycled gap\| ≤ 0.03 |
| **F** | Frequency | Sweep J_mem ∈ {0.0, 0.25, 0.5, 0.75, 1.0}; find peak-gap | peak at J_mem ∈ (0.30, 0.70) |
| **P** | Phase | Read u_D directly (not v_D); gap diag vs off | \|u_D gap\| ≤ 0.03 |

### Verdict tiers

- **STRONG PASS** — all five gates pass. The architecture's primitive set is operational end-to-end.
- **WEAK PASS** — S + R + P pass (substrate + rotation + cross-chirality). Transfer or Frequency degraded.
- **NULL** — R fails. The Z₃ cyclic shift is not detectable at Willow noise, falsifying Paper 35 Option A.

### Decisive gate

**R is the decisive test.** It asks: when I write label X, does the architecture return a state that recognises cycle(X) = X⁻¹ under the Z₃ Galois group? If yes, the compute + tunnel compose natively performs modular-3 ternary arithmetic, and the merkabit is a self-hosting quantum computer. If no, the decomposition into primitive operations is incomplete.

**Script:** `tesseract_quantum_implementation/willow/obs22_pentachoric.py`. Budget: ~140 QPU-min.

### Laptop simulation sanity baseline

Smoke test at n_trials=2, shots=256 (deliberately underpowered) already returns:

```
22-S (Substrate):       mean |<u|v>| = 0.484            PASS
22-R (Rotation):        cycled gap = +0.168 (+4.1 sigma) PASS
22-T (Transfer null):   cycled gap = -0.019              PASS
22-F (Frequency):       J_mem peak = 0.50                PASS
22-P (Phase/chirality): u_D gap    = +0.017 (+0.5 sigma) PASS

PENTACHORIC VERDICT: STRONG PASS (all five gates)
```

Full simulation at n_trials=10, shots=2048 reports cycled gap = +0.159 ± 0.07 (+2.3σ). Willow-realistic noise (p_depol = 0.003) projects to ~+0.06 ± 0.04; n_trials = 40 on hardware recommended for 3σ detection.

---

## Overall falsification structure

A single failing gate in Observable 22 falsifies one specific named primitive of the architecture:

| If this gate fails... | ...this primitive is falsified |
|---|---|
| S | The 4-spinor tesseract does not sustain coherence end-to-end on Willow noise |
| R | The compose of Papers 31–32 + memory tunnel does not implement a native Z₃ rotation |
| T | The tunnel is not the content-routing operator (some other mechanism is involved) |
| F | Memory write is not at a structural optimum (J_mem = 0.5 is accidental, not geometric) |
| P | Paper 31's u → v cross-chirality rule does not hold at Willow fidelity |

Passing all five is the hardware verdict that the merkabit is a primitive-complete quantum computer.

---

## Hardware submission discipline

Raw Willow job identifiers, counts histograms, and per-observable pass/fail verdicts will be committed to this repository within 48 hours of each hardware run. No threshold is mutable after this file's initial commit — any adjustment is tracked in git history, making post-hoc threshold changes visible to any reviewer.

This file's initial commit SHA is the timestamped anchor for the pre-registration.
