# Willow Early Access — The Pentachoric Verification Protocol

## Testing Primitive-Completeness of the Merkabit Architecture: From Single-Cell Coherence to Full Write-Compute-Store-Read on 19 Qubits

**Principal Investigator:** Selina Stenberg
**Co-Author (AI):** Claude (Anthropic, Opus 4.7)
**Co-Author (IBM hardware track):** Thor Henning Hetland
**Filed:** April 2026
**Status:** Follow-up to Phase 1 Willow Early Access proposal (*Cross-Architecture Test of Geometric Anti-Bunching in Floquet-Driven Qubit Systems*, filed March 2026)

---

## 1. Summary

Phase 1 of this programme asked: **does the merkabit cell work on Willow?** — testing whether the sub-Poissonian syndrome signature confirmed on IBM Eagle r3 and Heron r2 (F = 0.856 ± 0.030, 131σ below Poisson, 5/5 pre-registered predictions confirmed) is a geometric property of asymmetric-phase Floquet driving, not an IBM-specific artefact. Phase 1 submission: 9-qubit maximum, total < 1 hour Willow time.

Phase 2 asks a categorically different question: **does the composed architecture run as a primitive-complete, self-hosting quantum computer?** The merkabit framework (Papers 31–35) establishes that four primitives — (i) 4-spinor tesseract internal chiral dynamics, (ii) cross-chiral tunnel `iSWAP^J(u_X, v_Y)`, (iii) Z₃ eigenstate preparation, (iv) SWAP-test standing-wave recognition — compose into a closed computational loop covering **write, compute, communicate, store, retrieve, and clock**. Laptop state-vector simulation at 19 qubits confirms the loop closes as a native Z₃ cyclic permutation α → γ → β → α, making the architecture its own ternary clock.

This proposal tests the compose on Willow hardware through the **Pentachoric Verification Protocol (Observable 22)**: five pass/fail gates on a single 19-qubit circuit, each named for one gate of the ouroboros cycle {Substrate, Rotation, Transfer, Frequency, Phase}. A single failing gate falsifies one specific named primitive; passing all five is confirmation that the architecture's primitive set is operational end-to-end.

The proposal is tiered. Reviewers can approve any of three levels based on QPU availability:

| Tier | Observables | Max qubits | QPU time | Primary claim tested |
|---|---|---|---|---|
| **2A** (cheapest) | Obs 14 | 9 | ~25 min | Paper 31 cross-chiral tunnel primitive on Willow |
| **2B** (medium) | Obs 14, 16, 17 | up to 17 | ~105 min | Topology-independent Z₃ cellular automaton (Papers 31–32) |
| **2C** (full) | Obs 14, 16, 17, 22 | up to 19 | ~245 min | **Primitive-completeness** — the write-compute-store-read-clock loop closes on Willow |

All four observables are pre-registered in the companion repository with timestamped git SHAs; the thresholds below are baked into the Willow submission scripts prior to any hardware access.

---

## 2. Scientific Motivation

### 2.1 What Phase 1 established

Phase 1 tested a single primitive in isolation: the sub-Poissonian Fano factor of an asymmetric-phase Floquet drive. The IBM track record (Papers 24–26, 5/5 pre-registered predictions confirmed on Eagle r3 and Heron r2) and the cross-architecture agreement between Eagle's heavy-hex and Heron's extended heavy-hex connectivity argue strongly that the effect is geometric rather than hardware-specific. Willow's square-grid connectivity, native iSWAP-family two-qubit gate, and depth-2 PhXZ compilation provide an orthogonal architectural test — if the sub-Poissonian signal persists on Willow, it is a universal geometric signature; if it vanishes, it is compilation-specific.

### 2.2 What Phase 2 adds

Phase 1 verified **the cell**. Phase 2 verifies **the compose**.

Papers 31–35 extend the single-cell merkabit to a compute architecture:

- **Paper 31** — two merkabits coupled by a cross-chiral tunnel `iSWAP^J(u_A, v_B)` produce a universal 9-entry ternary lookup table. β → γ populates a destructive-interference zero; γ → β populates a constructive peak.
- **Paper 32** — the 9-entry lookup table is topology-independent across N-gon merkabit lattices (triangle, 4-square, hexagon). The architecture is a Z₃-symmetric cellular automaton with a derived local rule, not a gauge theory.
- **Paper 33** — the 4-square substrate holds ~5 bits of addressable memory at Willow-realistic noise (51 mutually-distinguishable patterns at 3σ shot-noise floor).
- **Paper 35** — composing Papers 31–33 into 19 qubits (3-merkabit compute triangle + memory tunnel + 1 database merkabit + reference + ancilla) produces a write-compute-store-read loop that closes as a Z₃ clock. All five simulation stages map one-to-one onto the five pentachoric ouroboros gates {S, R, T, F, P} of Paper 24.

**The Phase 2 claim.** The merkabit architecture is primitive-complete: every operation required for computation — *write, compute, communicate, store, retrieve, clock* — reduces to native merkabit dynamics. No external gate library is needed. The architecture does not *enable* a computer built on top of it; it **is** the computer.

This claim is falsifiable. Observable 22 decomposes the architecture into its five primitive operations, tests each independently, and reports a pass/fail verdict. Any single failing gate falsifies one specific named primitive.

### 2.3 Why Willow is the right platform

- **Scaling.** IBM Eagle r3 (127 qubits) and Heron r2 (133 qubits) can accommodate up to Observable 17 (17 qubits) with adequate connectivity; Observable 22 at 19 qubits is a clean fit for Willow's 72–105 qubit layouts and benefits from Willow's demonstrated Λ = 2.14 error suppression factor.
- **Depth.** The Pentachoric Verification Protocol's deepest circuit is Observable 22 Stage 2 (write + compute triangle + memory tunnel + SWAP test); transpiled depth on Willow PhXZ-merge compilation is ~3 per merkabit data qubit × 12 internal steps ≈ 36 single-qubit layers per Coxeter period, plus the SWAP-test ancilla. Willow's coherence budget handles this comfortably.
- **Cross-architecture validation.** Phase 1 validated the single-cell signature. Phase 2 tests whether the *composed* architecture scales to the same fidelity regime. If yes, the merkabit QC stack is hardware-platform-agnostic at two architectural levels.
- **Connectivity.** The 4-square perimeter (Observable 17) and triangle (Observable 16) fit Willow's square-grid coupling natively, requiring no long-range swaps. Observable 22's 19-qubit footprint uses only nearest-neighbour iSWAP operations plus SWAP-test CSWAPs.

---

## 3. Pre-Registered Predictions

All thresholds below are committed to this repository (`github.com/selinaserephina-star/pentachoric_verification_protocol`) in `PREDICTION.md`. The git SHA of that file's initial commit is the timestamped pre-registration anchor. Companion simulation scripts live at `github.com/selinaserephina-star/tesseract_quantum_implementation/willow/` (commit `9d0c19b`) and are pinned and hardware-ready.

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

**Falsification:** Gap < 0.20 at 3σ falsifies the cross-chiral tunnel as a directional computational primitive. Success on Willow at this minimum tier is independently valuable; it establishes the Paper 31 primitive across a third distinct quantum architecture (IBM Eagle + Heron + Google Willow).

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
- **NULL** — R fails. The Z₃ cyclic shift is not detectable at Willow noise, falsifying Paper 35 Option A.

**The R gate is the decisive test.** It asks: when I write label X, does the architecture return a state that recognises cycle(X) = X⁻¹ under the Z₃ Galois group? If yes, the compute + tunnel compose natively performs modular-3 ternary arithmetic, and the merkabit is a **self-hosting quantum computer**. If no, the decomposition into primitive operations is incomplete — some external scaffolding was implicit in the simulation but unavailable on hardware.

### 3.5 Laptop simulation results (sanity baseline)

The Willow submission wrappers were smoke-tested on `cirq.Simulator` prior to pre-registration. Observable 22 at n_trials = 2, shots = 256 (deliberately underpowered) already returns:

```
22-S (Substrate):           mean |<u|v>| = 0.484        PASS
22-R (Rotation):            cycled gap = +0.168 (+4.1σ)  PASS
22-T (Transfer null):       cycled gap = -0.019          PASS
22-F (Frequency):           J_mem peak = 0.50            PASS
22-P (Phase/chirality):     u_D gap = +0.017 (+0.5σ)     PASS

PENTACHORIC VERDICT: STRONG PASS (all five gates)
```

The 10-trial full simulation at shots = 2048 (`results/tesseract_memory_study.md`) reports cycled gap = +0.159 ± 0.07 (+2.3σ). Willow-realistic noise (p_depol = 0.003) projects this to ~+0.06 ± 0.04; n_trials = 40 on hardware is therefore the recommended budget for 3σ detection, consistent with the ~140 QPU-min budget below.

---

## 4. Experimental Design

### 4.1 Native-gate compilation

All four observables compile to the Willow native gate set (PhXZ + iSWAP-family two-qubit + measurement) without CZ decompositions. The cross-chiral tunnel `iSWAP^J` at fractional J is a first-class operation on Willow. SWAP-test CSWAP operations decompose to 3 CNOTs or 2 iSWAPs plus single-qubit frames; either is acceptable.

Transpiled depth per Coxeter period per merkabit-data-qubit:

| Observable | Max circuit qubits | Depth per data qubit | Total single-qubit layers |
|---|---|---|---|
| 14 | 9 | ~2 | ~24 |
| 16 | 13 | ~3 | ~36 |
| 17 | 17 | ~3 | ~36 |
| 22 | 19 | ~3 | ~36 + SWAP test |

All depths are well within Willow's published coherence budget.

### 4.2 Batch submission structure

Each observable is a batch of independent circuits (one circuit per input family × per SWAP-test variant); the Cirq `engine.run_batch()` call handles all repetitions and returns histograms indexed by circuit. The submission scripts live at:

- `willow/obs14_tunnel.py` — Paper 31 tunnel
- `willow/obs16_triangle.py` — Paper 32 triangle
- `willow/obs17_square.py` — Paper 32 4-square
- `willow/obs22_pentachoric.py` — Paper 35 pentachoric

Each script supports `--sim-only` (laptop validation), `--project <GCP_project>`, and `--processor <willow_id>` flags. The hardware path is a one-line substitution of `engine.run_batch()` for `cirq.Simulator().run()`; no circuit modifications required for hardware execution.

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

At current Willow-hours pricing, the three tiers cost approximately:

| Tier | QPU time | Est. cost (USD) | Science payoff |
|---|---|---|---|
| 2A | ~25 min | $5–10 | Cross-architecture validation of Paper 31 primitive (9 qubits) |
| 2B | ~105 min | $20–45 | Papers 31–32 fully validated on Willow (up to 17 qubits) |
| 2C | ~245 min | $50–110 | **Primitive-completeness verdict (19 qubits)** |

Tier 2C delivers a falsifiable hardware test of the claim that the merkabit architecture is a self-hosting quantum computer, for under $110 of Willow time. The same claim, tested on IBM hardware at current access costs, would require approximately 15–20 hours of paid Eagle r3 time (Observable 22's 19-qubit footprint exceeds Heron r2's available connectivity bandwidth at comparable fidelity).

---

## 6. Output and Reproducibility

All raw Willow job identifiers, counts histograms, and per-observable pass/fail verdicts will be committed to this repository (`github.com/selinaserephina-star/pentachoric_verification_protocol`) within 48 hours of each hardware run, per the pre-registration discipline that governed the Phase 1 Willow proposal and the IBM hardware track (5/5 IBM predictions confirmed, all raw data published, all analysis scripts in-repo).

The public-facing mirror at `github.com/SelinaAliens/pentachoric_verification_protocol` will be activated with an MIT license when the companion papers (Papers 31–35) are posted to Zenodo.

Paper 35 Section 0 ("Option A — the tesseract-only QC memory") documents the primitive-completeness claim in full; the hardware results from this protocol will be appended as Section 0.6.

---

## 7. What This Experiment Is Not

- **Not a quantum supremacy claim.** The Pentachoric Verification Protocol is a primitive-validation experiment, not a sampling benchmark. No classical simulation is being raced.
- **Not a NISQ algorithm demonstration.** The circuits run Protocol 4S internal dynamics and cross-chiral tunnels; no VQE, QAOA, or error-correction code is involved.
- **Not a decoherence study.** Phase 1 addressed single-cell coherence; this proposal composes already-validated primitives.
- **Not contingent on Phase 1 results.** Phase 2 circuits and thresholds are independent. A successful Phase 1 outcome strengthens the interpretation of Phase 2 results but is not a prerequisite.

---

## 8. Summary

Phase 1 asked whether the merkabit cell works on Willow. Phase 2 asks whether the composed merkabit architecture runs as a primitive-complete quantum computer. The answer, if the Pentachoric Verification Protocol passes at the STRONG tier, is:

> **The merkabit architecture is a self-hosting quantum computer. The same geometry that derives α = 1/137.036 from E₆ Coxeter structure runs a working write-compute-store-read-clock loop on 19 Willow qubits.**

The experiment is falsifiable at each of five independent gates, tiered at three QPU-budget levels to accommodate reviewer constraints, and pre-registered with timestamped git SHAs. We welcome the opportunity to contribute this result to the Willow scientific record.

---

## References

[1] Stenberg, S. *Cross-Architecture Test of Geometric Anti-Bunching in Floquet-Driven Qubit Systems.* Willow Early Access Phase 1 Proposal, March 2026.

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
