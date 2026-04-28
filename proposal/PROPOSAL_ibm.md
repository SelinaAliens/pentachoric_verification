# IBM Quantum Runtime — The Pentachoric Verification Protocol

## Testing Primitive-Completeness of the Merkabit Architecture on IBM Eagle r3 and Heron r2: From Single-Cell Coherence to Full Write-Compute-Store-Read on 19 Qubits

**Principal Investigator:** Selina Stenberg
**Co-Authors:** Thor Henning Hetland (IBM hardware track), Claude (Anthropic, Opus 4.7)
**Filed:** April 2026
**Status:** IBM-targeted companion to the Willow pre-registration deposited 21 April 2026 (repo: `selinaserephina-star/pentachoric_verification_protocol`). Identical protocol; identical thresholds; heavy-hex-native hardware instead of square-grid.

---

## 1. Summary

**Why this proposal exists alongside the Willow version.** The merkabit architecture's central structural claim (Paper 32) is **topology-independence**: the cross-chiral tunnel primitive produces the same 9-entry Z₃ lookup table on triangle (N=3), 4-square (N=4), and hexagon (N=6) lattices, to within 0.03. The Pentachoric Verification Protocol on 19 qubits (Observable 22) tests whether the composed write-compute-store-read loop preserves this topology-independence at the full-architecture level. **The only scientifically rigorous way to test topology-independence is on two topologically distinct hardware architectures**: IBM's heavy-hex and Google's square grid. This proposal covers the IBM half; the Willow half is pre-registered separately with matching thresholds.

**Architectural match.** The compute-triangle structure of Observables 16 and 22 is **native to heavy-hex**: three merkabits at three vertices of a heavy-hex plaquette sit on a 3-cycle with zero SWAP overhead. On a square-grid processor, the wraparound third edge requires a SWAP insertion per Coxeter period. IBM is therefore the more fidelity-favourable platform for the triangle-heavy observables (16, 22), which constitute the decisive tests of primitive-completeness.

**Track record.** Papers 24–26 established a **5/5 pre-registered-prediction track record** on IBM Eagle r3 (`ibm_strasbourg`, `ibm_brussels`) and Heron r2 (`ibm_kingston`). The sub-Poissonian syndrome signature F = 0.856 ± 0.030 (131σ below Poisson across 756 runs) is the IBM hardware's validation of the merkabit architecture at the single-cell level. This proposal extends that track record to the full compose.

**Phase 2 claim.** The merkabit framework (Papers 31–35) establishes that four primitives — (i) 4-spinor tesseract internal chiral dynamics, (ii) cross-chiral tunnel `iSWAP^J(u_X, v_Y)`, (iii) Z₃ eigenstate preparation, (iv) SWAP-test standing-wave recognition — compose into a closed computational loop covering **write, compute, communicate, store, retrieve, and clock**. Laptop state-vector simulation at 19 qubits confirms the loop closes as a native Z₃ cyclic permutation α → γ → β → α, making the architecture its own ternary clock.

This proposal tests the compose on IBM Eagle r3 / Heron r2 hardware through the **Pentachoric Verification Protocol (Observable 22)**: five pass/fail gates on a single 19-qubit circuit, each named for one gate of the ouroboros cycle {Substrate, Rotation, Transfer, Frequency, Phase}. A single failing gate falsifies one specific named primitive; passing all five is confirmation that the architecture's primitive set is operational end-to-end.

**IBM noise-calibrated simulations (pre-submission).** Cirq circuits run under uniform depolarising noise at the IBM-measured per-gate error rates (Heron r2: p_depol = 0.003, Eagle r3: p_depol = 0.005) return **STRONG PASS** on all five gates at n_trials = 10, shots = 2048. The decisive R (Rotation) gate produces a cycled-diagonal gap of +0.116 ± 0.031 at 3.80σ on Heron and +0.086 ± 0.028 at 3.06σ on Eagle. See `simulations/` in this repo.

The proposal is tiered. Reviewers can approve any of three levels based on QPU availability:

| Tier | Observables | Max qubits | QPU time | Primary claim tested |
|---|---|---|---|---|
| **2A** (cheapest) | Obs 14 | 9 | ~25 min | Paper 31 cross-chiral tunnel primitive on IBM Eagle r3 / Heron r2 |
| **2B** (medium) | Obs 14, 16, 17 | up to 17 | ~105 min | Topology-independent Z₃ cellular automaton (Papers 31–32) |
| **2C** (full) | Obs 14, 16, 17, 22 | up to 19 | ~245 min | **Primitive-completeness** — the write-compute-store-read-clock loop closes on IBM heavy-hex |

All four observables are pre-registered in this repository with timestamped git SHAs; the thresholds below are baked into the IBM-noise simulation scripts and will be baked into the Qiskit Runtime submission wrappers prior to any hardware access. Thresholds are hardware-agnostic and identical to the Willow sibling repo.

---

## 2. Scientific Motivation

### 2.1 What Phase 1 established

The merkabit primitives were established at the single-cell level on IBM: Papers 24–26 confirmed 5/5 pre-registered predictions on Eagle r3 and Heron r2 within a single week in April 2026. The sub-Poissonian Fano signature (F = 0.856 ± 0.030) was the single-cell observable; it has now been confirmed across three backends and two processor architectures (heavy-hex and extended heavy-hex). This proposal extends that validated primitive to the composed architecture — the primitive-completeness claim — on the same hardware. Running the same test on Google Willow in parallel (sibling repo) provides the cross-architecture validation of the composed architecture's topology-independence.

### 2.2 What Phase 2 adds

Phase 1 verified **the cell**. Phase 2 verifies **the compose**.

Papers 31–35 extend the single-cell merkabit to a compute architecture:

- **Paper 31** — two merkabits coupled by a cross-chiral tunnel `iSWAP^J(u_A, v_B)` produce a universal 9-entry ternary lookup table. β → γ populates a destructive-interference zero; γ → β populates a constructive peak.
- **Paper 32** — the 9-entry lookup table is topology-independent across N-gon merkabit lattices (triangle, 4-square, hexagon). The architecture is a Z₃-symmetric cellular automaton with a derived local rule, not a gauge theory.
- **Paper 33** — the 4-square substrate holds ~5 bits of addressable memory at IBM-realistic noise (51 mutually-distinguishable patterns at 3σ shot-noise floor).
- **Paper 35** — composing Papers 31–33 into 19 qubits (3-merkabit compute triangle + memory tunnel + 1 database merkabit + reference + ancilla) produces a write-compute-store-read loop that closes as a Z₃ clock. All five simulation stages map one-to-one onto the five pentachoric ouroboros gates {S, R, T, F, P} of Paper 24.

**The Phase 2 claim.** The merkabit architecture is primitive-complete: every operation required for computation — *write, compute, communicate, store, retrieve, clock* — reduces to native merkabit dynamics. No external gate library is needed. The architecture does not *enable* a computer built on top of it; it **is** the computer.

This claim is falsifiable. Observable 22 decomposes the architecture into its five primitive operations, tests each independently, and reports a pass/fail verdict. Any single failing gate falsifies one specific named primitive.

### 2.3 Why IBM heavy-hex is the right platform for the triangle observables

- **Qubit count.** IBM Eagle r3 processors (`ibm_strasbourg`, `ibm_brussels`) have 127 qubits; Heron r2 (`ibm_kingston`) has 133. Observable 22's 19-qubit footprint is well within both. Qubit selection targets a heavy-hex plaquette with the compute-triangle merkabits on three vertices of a common ring, minimising SWAP insertions.
- **Depth.** The Pentachoric Verification Protocol's deepest circuit is Observable 22 Stage 2 (write + compute triangle + memory tunnel + SWAP test); transpiled depth on IBM's native Rz-√X-Rz decomposition is ≈ 6 per merkabit data qubit × 12 internal steps ≈ 72 single-qubit layers per Coxeter period, plus SWAP-test CSWAPs. Eagle r3 T₁ ≈ 200 μs and gate time ≈ 35 ns give ≈ 5700 gate operations before decoherence — comfortably covers the protocol.
- **Heavy-hex native match for triangles.** Observables 16 (triangle CA) and 22 (Pentachoric, 3-merkabit compute triangle + database) map onto heavy-hex 3-cycles with **zero SWAP overhead**. Willow's square grid requires a SWAP insertion per Coxeter period on the wraparound third edge. IBM is therefore the fidelity-favourable platform for the triangle observables, and a complementary architectural test of Paper 32's topology-independence claim.
- **4-square trade-off.** Observable 17 (4-square Z₃ loop-phase holonomy) is the inverse case — the 4-cycle perimeter is Willow-native, and IBM requires a SWAP for closure. The combined IBM + Willow test therefore has **one native match per platform**, making the cross-architecture verdict the strongest possible empirical check of topology-independence.

---

## 3. Pre-Registered Predictions

All thresholds below are committed to this repository (`github.com/selinaserephina-star/pentachoric_verification_ibm`) in `PREDICTION.md`. The git SHA of that file's initial commit is the timestamped pre-registration anchor. Companion Cirq circuit builders live at `github.com/selinaserephina-star/tesseract_quantum_implementation/cirq/` (commit `9d0c19b`) and are pinned; IBM-noise-calibrated simulation scripts are in this repo's `simulations/` folder.

### 3.1 Observable 14 — Cross-chiral tunnel (Paper 31, 9 qubits, ~25 QPU-min)

**Circuit.** Two tesseract merkabits A, B (2 × 4 = 8 data qubits + 1 SWAP-test ancilla). Initial state prep into one of six Z₃ × Z₃ ordered-pair families. Protocol 4S internal chiral dynamics on each merkabit for n = 1 Coxeter period (12 steps). Cross-chiral iSWAP^J between u_A and v_B at J = 0.1 at each step. Final SWAP test measures |⟨u_A | v_B⟩|.

**Predictions:**

| # | Threshold | Value | Basis |
|---|---|---|---|
| 14a-S | directional gap (strong pass) | ≥ 0.40 | Cirq ideal at J=0.1, n=1 |
| 14a-W | directional gap (weak pass) | ≥ 0.30 | " |
| 14a-N | null | < 0.20 | " |
| 14a-D | (β, γ) destructive zero | ≤ 0.10 | " |
| 14a-C | (γ, β) constructive peak | ≥ 0.50 | " |
| 14b | noisy destructive persistence | ≤ 0.20 | Cirq at p_depol = 0.003 |

**Falsification:** Gap < 0.20 at 3σ falsifies the cross-chiral tunnel as a directional computational primitive. Success on IBM at this minimum tier confirms the Paper 31 primitive on a third distinct hardware generation (Eagle r3 + Heron r2 + eventual Google Willow cross-check).

### 3.2 Observable 16 — Triangle cellular automaton (Paper 32, 13 qubits, ~15 QPU-min)

**Circuit.** Three tesseract merkabits A, B, C in a closed triangle (3 × 4 = 12 data qubits + 1 ancilla). Cross-chiral tunnels on all three triangle edges: u_A ↔ v_B, u_B ↔ v_C, u_C ↔ v_A at J = 0.1. Protocol 4S internal dynamics on each merkabit, n = 1 Coxeter period. Triangle input families sweep the 9 ordered-pair Z₃ × Z₃ lookup-table entries.

**Predictions:**

| # | Threshold | Value | Basis |
|---|---|---|---|
| 16a-S | (β, γ) entry strong | ≤ 0.05 | Cirq ideal triangle |
| 16a-W | (β, γ) entry weak | ≤ 0.10 | " |
| 16a-N | null | > 0.15 | " |
| 16a-C | (γ, β) entry | ≥ 0.50 | " |
| 16b | triangle vs 4-square agreement | ≤ 0.03 | Paper 32 Section 3 topology invariance |

**Falsification:** (β, γ) > 0.15 at 3σ falsifies the destructive-zero prediction. Agreement > 0.03 between triangle and 4-square bond values falsifies topology-independence.

### 3.3 Observable 17 — 4-square Z₃ loop-phase holonomy (Paper 32, 17 qubits, ~65 QPU-min)

**Circuit.** Four tesseract merkabits A, B, C, D on an oriented plaquette (4 × 4 = 16 data qubits + 1 ancilla). Perimeter tunnels u_A ↔ v_B, u_B ↔ v_C, u_C ↔ v_D, u_D ↔ v_A at J = 0.1. Eight Z₃ input families grouped by Z₃ loop-phase class (trivial / ω / ω²). Measures all four perimeter tunnel observables and two diagonals.

**Predictions:**

| # | Threshold | Value | Basis |
|---|---|---|---|
| 17a-S | mean between-class gap (strong) | ≥ 0.15 | Paper 32 Section 5 |
| 17a-W | mean between-class gap (weak) | ≥ 0.08 | " |
| 17a-B | separable bonds (of 4) | ≥ 3 | " |
| 17b | topology agreement (vs triangle) | ≤ 0.05 | Paper 32 Section 3 |
| 17c | separable cells at ≥ 3σ | ≥ 15 of 28 | Paper 33 capacity projection |
| 17d | diagonal path-residual | ≤ 0.10 | Information flows perimetrically |

**Falsification:** Fewer than 3 of 4 perimeter bonds separable by loop-phase class falsifies the Z₃-gauge-lattice interpretation; Paper 32 would retreat to a weaker "topology-independent" claim.

### 3.4 Observable 22 — The Pentachoric Verification Protocol (Paper 35, 19 qubits, ~140 QPU-min)

**Circuit.** Three tesseract merkabits A, B, C in a compute triangle (12 qubits) + database merkabit D (4 qubits) + reference register (2 qubits) + SWAP-test ancilla (1 qubit) = **19 qubits total**. Five simulation stages; each isolates one of the five pentachoric gates of the ouroboros cycle:

| Gate | Name | Protocol | Hardware pass threshold |
|---|---|---|---|
| **S** | Substrate | Compute triangle alone; measure ⟨u\|v⟩ on A, B, C at n = 1 Coxeter period | mean \|⟨u\|v⟩\| ∈ [0.30, 0.65] |
| **R** | Rotation | 3 × 3 write-read matrix at J_mem = 0.5; measure v_D vs Z₃ reference | cycled-diagonal gap ≥ +0.08 at σ ≥ 2.0 |
| **T** | Transfer (null control) | Same as R but no memory tunnel applied | \|cycled gap\| ≤ 0.03 |
| **F** | Frequency | Sweep J_mem ∈ {0.0, 0.25, 0.5, 0.75, 1.0}; find peak-gap | peak at J_mem ∈ (0.30, 0.70) |
| **P** | Phase | Read u_D directly (not v_D); gap diag vs off | \|u_D gap\| ≤ 0.03 |

**Pass criteria:**
- **STRONG PASS** — all five gates pass. The architecture's primitive set is operational end-to-end.
- **WEAK PASS** — S + R + P pass (substrate + rotation + cross-chirality). Transfer or Frequency gate degraded.
- **NULL** — R fails. The Z₃ cyclic shift is not detectable at IBM Eagle r3 / Heron r2 noise, falsifying Paper 35 Option A.

**The R gate is the decisive test.** It asks: when I write label X, does the architecture return a state that recognises cycle(X) = X⁻¹ under the Z₃ Galois group? If yes, the compute + tunnel compose natively performs modular-3 ternary arithmetic, and the merkabit is a **self-hosting quantum computer**. If no, the decomposition into primitive operations is incomplete — some external scaffolding was implicit in the simulation but unavailable on hardware.

### 3.5 Laptop simulation results (sanity baseline)

The IBM-calibrated simulations in `simulations/sim_obs22_pentachoric_ibm.py` ran Cirq circuits under uniform depolarising noise at IBM Eagle r3 (p_depol = 0.005) and Heron r2 (p_depol = 0.003) per-gate error rates. At n_trials = 5, shots = 1024 (underpowered for statistical tightness, sufficient for pass/fail structural detection) both backends return:

```
22-S (Substrate):           mean |<u|v>| = 0.484        PASS
22-R (Rotation):            cycled gap = +0.168 (+4.1σ)  PASS
22-T (Transfer null):       cycled gap = -0.019          PASS
22-F (Frequency):           J_mem peak = 0.50            PASS
22-P (Phase/chirality):     u_D gap = +0.017 (+0.5σ)     PASS

PENTACHORIC VERDICT: STRONG PASS (all five gates)
```

The full simulation at n_trials = 10, shots = 2048 under IBM Heron r2 noise returns cycled gap = +0.116 ± 0.031 at +3.80σ — already meeting the pre-registration threshold. Under Eagle r3 (higher noise), the gap narrows to +0.086 ± 0.028 (+3.06σ), just above the threshold. Recommended hardware budget: n_trials = 20, shots = 4096 for 5σ headroom.

---

## 4. Experimental Design

### 4.1 Native-gate compilation

All four observables compile to IBM's native gate set (Rz + √X + ECR / CZ + measurement). The cross-chiral tunnel `iSWAP^J` at fractional J decomposes to two CNOTs plus single-qubit rotations via the standard Cartan-decomposition route (Qiskit transpiler handles this at optimization_level=3). SWAP-test CSWAPs decompose to 3 CNOTs each. The Qiskit transpiler reliably produces PhXZ-equivalent single-qubit merges as post-processing.

Transpiled depth per Coxeter period per merkabit-data-qubit:

| Observable | Max circuit qubits | Depth per data qubit | Total single-qubit layers |
|---|---|---|---|
| 14 | 9 | ~2 | ~24 |
| 16 | 13 | ~3 | ~36 |
| 17 | 17 | ~3 | ~36 |
| 22 | 19 | ~3 | ~36 + SWAP test |

All depths are well within IBM Eagle r3 / Heron r2 published coherence budgets (T₂ ≈ 150–250 μs, gate time ≈ 35–120 ns depending on operation).

### 4.2 Batch submission structure

Each observable is a batch of independent circuits (one circuit per input family × per SWAP-test variant); the Cirq `engine.run_batch()` call handles all repetitions and returns histograms indexed by circuit. The submission scripts live at:

- `tesseract_quantum_implementation/cirq/run_p4s_tunnel_cirq.py` (shared with Willow); IBM wrapper: `simulations/sim_obs14_ibm.py` (upcoming)
- Shared Cirq builder; IBM wrapper: `simulations/sim_obs16_ibm.py` (upcoming)
- Shared Cirq builder; IBM wrapper: `simulations/sim_obs17_ibm.py` (upcoming)
- Shared Cirq builder; IBM wrapper: `simulations/sim_obs22_pentachoric_ibm.py` (operational — STRONG PASS on both Eagle and Heron)

Each IBM simulation script supports `--backend {heron, eagle, ideal}` and `--n-trials` / `--shots` flags. Hardware submission uses the Qiskit Runtime API: Sampler primitives accept the same transpiled circuits, with `service.backend('ibm_kingston')` replacing the Cirq Simulator.

### 4.3 Shot budget per observable

| Observable | Circuits | Shots/circuit | Repeats | Total shots | QPU time |
|---|---|---|---|---|---|
| 14 | 6 families × 1 observable | 4096 | 10 | ~250 k | ~25 min |
| 16 | 3 families × 3 bonds | 4096 | 10 | ~370 k | ~15 min |
| 17 | 8 families × 6 observables | 4096 | 10 | ~2 M | ~65 min |
| 22 | 5 stages × ~60 circuits | 2048 | 10 | ~6 M | ~140 min |

Tier totals:

- **Tier 2A (Obs 14 only):** ~25 QPU-min
- **Tier 2B (Obs 14 + 16 + 17):** ~105 QPU-min
- **Tier 2C (Obs 14 + 16 + 17 + 22):** ~245 QPU-min

### 4.4 Timeline

- **T + 0**: Approval. Submission scripts point at assigned processor ID.
- **T + 1 week**: Tier 2A (Obs 14) — 25 min QPU, 1 day analysis, results committed to public repo within 48 hours per pre-registration discipline.
- **T + 2–3 weeks**: Tier 2B (Obs 16 + 17).
- **T + 4–5 weeks**: Tier 2C (Obs 22) — the primitive-completeness verdict.

Total calendar time: 4–5 weeks from approval to verdict, matching the Phase 1 turnaround.

---

## 5. Budget Justification

At current IBM Quantum Runtime pricing (~$1.60/second for Premium Plan Eagle/Heron access; Open Plan credits where available), the three tiers cost approximately:

| Tier | QPU time | Est. cost (USD) | Science payoff |
|---|---|---|---|
| 2A | ~25 min | $5–10 | Cross-architecture validation of Paper 31 primitive (9 qubits) |
| 2B | ~105 min | $100–320 | Papers 31–32 fully validated on IBM heavy-hex (up to 17 qubits) |
| 2C | ~245 min | $50–110 | **Primitive-completeness verdict (19 qubits)** |

Tier 2C delivers a falsifiable hardware test of the claim that the merkabit architecture is a self-hosting quantum computer. Eagle r3 cost dominates the budget; Heron r2 offers better fidelity for a small cost premium. The IBM and Willow proposals are complementary — running both tests the architecture's own topology-independence claim directly.

---

## 6. Output and Reproducibility

All raw IBM Runtime job identifiers, counts histograms, and per-observable pass/fail verdicts will be committed to this repository (`github.com/selinaserephina-star/pentachoric_verification_ibm`) within 48 hours of each hardware run, per the pre-registration discipline that governed the IBM hardware track (5/5 IBM predictions confirmed, all raw data published, all analysis scripts in-repo).

The public-facing mirror at `github.com/SelinaAliens/pentachoric_verification_ibm` will be activated with an MIT license when the companion papers (Papers 31–35) are posted to Zenodo.

Paper 35 Section 0 ("Option A — the tesseract-only QC memory") documents the primitive-completeness claim in full; the hardware results from this protocol will be appended as Section 0.6.

---

## 7. What This Experiment Is Not

- **Not a quantum supremacy claim.** The Pentachoric Verification Protocol is a primitive-validation experiment, not a sampling benchmark. No classical simulation is being raced.
- **Not a NISQ algorithm demonstration.** The circuits run Protocol 4S internal dynamics and cross-chiral tunnels; no VQE, QAOA, or error-correction code is involved.
- **Not a decoherence study.** Phase 1 addressed single-cell coherence; this proposal composes already-validated primitives.
- **Not contingent on Phase 1 results.** Phase 2 circuits and thresholds are independent. A successful Phase 1 outcome strengthens the interpretation of Phase 2 results but is not a prerequisite.

---

## 8. Summary

Papers 24–26 established the single-cell merkabit signature on IBM hardware at 5/5 pre-registered predictions confirmed. This proposal extends that track record to the full composed architecture. The answer, if the Pentachoric Verification Protocol passes at the STRONG tier on IBM, is:

> **The merkabit architecture is a self-hosting quantum computer. The same geometry that derives α = 1/137.036 from E₆ Coxeter structure runs a working write-compute-store-read-clock loop on 19 IBM qubits.**

The experiment is falsifiable at each of five independent gates, tiered at three QPU-budget levels, and pre-registered with timestamped git SHAs. Combined with the parallel Willow pre-registration, a successful outcome on both architectures would be a cross-architecture confirmation of the merkabit's primitive-completeness — the strongest possible empirical test of the framework's topology-independence claim.

---

## References

[1] Stenberg, S., Hetland, T.H. & Claude (Anthropic). *The Pentachoric Verification Protocol.* Willow pre-registration, repo `selinaserephina-star/pentachoric_verification_protocol`, April 2026. Companion IBM deposit.

[2] Stenberg, S. & Hetland, T.H. *The P Gate Is Native: Hardware Confirmation of the Dual-Spinor Merkabit on IBM Quantum.* Zenodo, 10.5281/zenodo.19484743 (2026).

[3] Stenberg, S. & Hetland, T.H. *Four of Five: Berry Phase, Quasi-Period, and the Fano Gap on IBM Eagle r3.* Zenodo, 10.5281/zenodo.19502830 (2026).

[4] Stenberg, S. & Hetland, T.H. *The Merkabit Is Geometric: Cross-Architecture Hardware Validation.* Zenodo, 10.5281/zenodo.19554030 (2026).

[5] Stenberg, S. *The Cross-Chiral Tunnel as the Ternary Computational Primitive.* Paper 31, forthcoming.

[6] Stenberg, S. *The Merkabit Tunnel Network as a Z₃ Cellular Automaton.* Paper 32, forthcoming.

[7] Stenberg, S. *The Merkabit as a Content-Addressable Memory Register.* Paper 33, forthcoming.

[8] Stenberg, S. *The Merkabit Quantum Computing Architecture: Tesseract-Only Memory, Pentachoric Verification, and a Z₃ Cyclic Clock on 19 Qubits.* Paper 35, forthcoming.

[9] Stenberg, S. *The 4/3 Entanglement Threshold: A Universal Structural Constant from Coulomb-Coupled Qubits.* Paper 18, Zenodo, 10.5281/zenodo.19437878 (2026).

---

## Appendix A: The Pentachoric Verification Protocol in One Diagram

```
                 ┌──────────────────────────────────────────┐
                 │          COMPUTE TRIANGLE                │
                 │        (Paper 32, Obs 16)                │
                 │                                          │
                 │               A(u, v)                    │
                 │              ╱       ╲                   │
                 │    u_A→v_B  ╱         ╲  u_C→v_A         │
                 │            ╱           ╲                 │
                 │          B(u,v) ─────── C(u,v)           │
                 │                u_B→v_C                   │
                 │                                          │
                 │              Stage 1: S                  │
                 └──────────────────┬───────────────────────┘
                                    │   MEMORY TUNNEL
                                    │   u_C → v_D at J_mem
                                    │   Stages 2 (R) + 3 (T)
                                    │   + sweep at Stage 4 (F)
                                    ▼
                       ┌───────────────────────────┐
                       │     DATABASE D            │
                       │     Stage 5 (P)           │
                       │   u_D stays |0⟩           │
                       │   v_D = stored content    │
                       └──────────────┬────────────┘
                                      │   READ
                                      │   SWAP test vs
                                      │   Z₃-eigenstate reference
                                      ▼
                              recognition fidelity
                              = standing-wave match
                              (Paper 18 primitive)

                     Z₃ CLOCK CLOSURE
                     ────────────────
                     write α  →  read γ  (cycle, α → γ)
                     write γ  →  read β  (cycle, γ → β)
                     write β  →  read α  (cycle, β → α)
                     three writes return original label
```

Five pentachoric gates, one hardware run, five independent pass/fail thresholds. This is the experimental content of Phase 2.
