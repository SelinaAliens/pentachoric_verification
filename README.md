# Pentachoric Verification

Reference implementation for the **Pentachoric Verification Protocol (PVP)**
— a 19-qubit primitive-completeness test of the merkabit architecture — and
its 28-qubit ternary-spectrum extension. Companion code, raw simulation data,
hardware proposals, and pre-registered hardware-deployment scripts for two
papers in the Merkabit Research Series:

| Paper | Title | Headline result |
|-------|-------|-----------------|
| **33** | *The Merkabit Quantum Computing Architecture: Tesseract-Only Memory, Pentachoric Verification, and a Native Z₃ Cyclic Clock on 19 Qubits* | Native Z₃ cyclic clock α → γ → β → α emerges from composing three triangle-edge tunnels with one memory tunnel. Cycled-diagonal gap +0.110 (3.56 σ) at IBM Heron r2 noise / +0.086 (3.06 σ) at Eagle r3 |
| **34** | *The Ternary Spectrum: Cyclotomic Z₃ Structure in Coupled Merkabit Triangles* | 28-qubit double-triangle entropy spectrum is period-12 (Coxeter) to machine precision; FFT power concentrated in the fundamental + Z₂ subharmonic only — the cyclotomic Z₃ representation theory of the h(E₆) = 12 master clock |

Paper 33 advances a **categorically stronger claim** than the substrate-of-physics
claim of the Merkabit base papers (1–28) and the hardware-confirmation claim of
Papers 24–26: that the merkabit architecture is a **primitive-complete,
self-hosting quantum computer**. Every operation required for computation —
write, compute, communicate, store, retrieve, and clock — reduces to the same
cross-chiral-tunnel primitive at a different coupling strength (J_intra = 0.1
inside the compute triangle, J_mem = 0.5 on the memory bus). No external gate
library is required.

Paper 34 extends the architecture to two coupled compute triangles sharing a
single database merkabit, and reports the **first measured spectrum of the 137
ternary architecture**. Paper 7 located all 29 known Riemann zeros in the
31 binary architecture; the present paper confirms that the complementary 137
ternary sector yields cyclotomic Z₃ — the representation theory of the Z₃
subgroup of the Coxeter clock. The two strata together exhaust the PSL(2,7)
decomposition.

## Architectural context

This work composes the primitives developed in the companion repository
[`SelinaAliens/tesseract_quantum_implementation`](https://github.com/SelinaAliens/tesseract_quantum_implementation) (Papers 31, 32):

- **Paper 31** — cross-chiral tunnel `iSWAP^J(u_A, v_B)` between two
  4-spinor tesseract merkabits. Universal 9-entry Z₃ × Z₃ lookup table;
  destructive zero at (β, γ); constructive peak at (γ, β).
- **Paper 32** — topology-independence of the lookup table across triangle,
  4-square, and hexagon rings; falsification of Z₃ plaquette holonomy.

Paper 33 composes those primitives into a 19-qubit closed loop. Paper 34
couples two such loops through a shared database merkabit.

The full forcing chain is consolidated in the capstone:

> *Paper 30: A Unified Theory from E₆ Coxeter Geometry* — Stenberg (2026), [Zenodo 19690395](https://doi.org/10.5281/zenodo.19690395).

Hardware confirmation of the 2-spinor substrate (5/5 pre-registered observables
on IBM Eagle r3 and Heron r2) is reported in Papers 24–26.

## Repository layout

```
README.md             this file
LICENSE               MIT

paper_33_pvp_19q/                         Paper 33 — 19-qubit Pentachoric Verification
  cirq/run_p4s_compute_store_cirq.py        ideal / Heron / Eagle simulation
  cirq/run_p4s_distinguishability_cirq.py   stage-A sanity check
  willow/obs22_pentachoric.py               Observable 22 hardware deployment (Willow)
  willow/_engine_wrapper.py                 Engine-client adapter
  ibm_sim/sim_obs22_pentachoric_ibm.py      IBM Heron / Eagle noise-calibrated simulation (v1)
  ibm_sim/sim_obs22_pentachoric_ibm_v2.py   v2: corrected statistics, separately scaled 2q noise,
                                            ancilla readout error, parabolic F-gate criterion
  ibm_sim/fine_F_sweep_ideal.py             cycled-gap landscape map; decides peak vs plateau
  ibm_sim/fine_F_sweep_peierls_test.py      high-statistics test of plateau ceiling = 1/6
  ibm_sim/plateau_exact_search.py           machine-precision plateau ceiling + closed-form search
  results/                                  ~23 JSON outputs (compute_store + IBM v1/v2 + F-sweeps)
  figures/                                  five PVP figures + figure-generation script
                                              p33_fig1_closed_loop.png
                                              p33_fig2_architecture.png
                                              p33_fig3_z3_clock.png
                                              p33_fig4_five_stages.png
                                              p33_fig5_cross_platform.png

paper_34_ternary_spectrum_28q/            Paper 34 — 28-qubit double-triangle ternary spectrum
  cirq/run_p4s_double_triangle_cirq.py      Stage A / B / C (synchronous / interleaved / sweep)
  results/                                  4 JSON outputs (stage A, B-mode1, B-mode2, C)
  figures/                                  four spectrum figures + figure-generation script
                                              p34_fig1_architecture.png
                                              p34_fig2_entropy_spectrum.png
                                              p34_fig3_fft.png
                                              p34_fig4_stratum_correspondence.png

paper/                                    Paper drafts and master docx
  paper_33_draft.md, Paper_33.docx
  paper_34_draft.md, Paper_34.docx

proposal/                                 Hardware-time proposals
  PROPOSAL_ibm.md, PREDICTION_ibm.md, RESULTS_ibm.md
  PROPOSAL_willow.md, PREDICTION_willow.md, README_willow_proposal.md
```

## Hardware observables — pre-registered

| Observable | Paper | Qubits | QPU-min | Script |
|---|---|---|---|---|
| **22** — Pentachoric Verification Protocol | **33** | 19 | ~140 | [`paper_33_pvp_19q/willow/obs22_pentachoric.py`](paper_33_pvp_19q/willow/obs22_pentachoric.py) |
| **23** — Pentachoric-Lock Spectrum (commensurate, Regime 2) | **34** | 28 | (sim only)* | [`paper_34_ternary_spectrum_28q/cirq/run_p4s_double_triangle_cirq.py`](paper_34_ternary_spectrum_28q/cirq/run_p4s_double_triangle_cirq.py) |
| **24** — Incommensurate-frequency follow-up (Regime 3 prediction) | **34** | 28 | (sim only)* | committed; sweep awaits scheduling |

*28-qubit observables (23, 24) are presently classical-simulation pre-registrations. Hardware deployment scripts will be added as larger backends become available.

Pentachoric Verification Protocol — five sub-tests on a single 19-qubit circuit, each named for one gate of the ouroboros cycle {S, R, T, F, P}:

| Stage | Gate | Pass criterion |
|---|---|---|
| 1 | **S** — Substrate | mean `\|⟨u\|v⟩\|` ∈ [0.30, 0.65] (ideal attractor ≈ 0.47) |
| 2 | **R** — Rotation | cycled-diagonal gap > +0.08 at ≥ 2 σ (the central Z₃ result) |
| 3 | **T** — Transfer | tunnel coherence preserved across the memory bus |
| 4 | **F** — Frequency | period matches Coxeter clock T_CYCLE = 12 |
| 5 | **P** — Phase | chiral asymmetry preserved (forward vs. inverse) |

Pre-submission Cirq simulations under uniform depolarising noise at IBM-calibrated rates:

- **Heron r2** (p_depol = 0.003): cycled gap **+0.110 ± 0.031 at 3.56 σ** — STRONG PASS
- **Eagle r3** (p_depol = 0.005): cycled gap **+0.086 ± 0.028 at 3.06 σ** — STRONG PASS

All five gates pass at both noise levels at n_trials = 10, shots = 2048.

Hardware targets: **IBM Eagle r3 / Heron r2** (heavy-hex native to the
compute-triangle topology) and **Google Willow** (square grid; cross-architecture
test of topology-independence at the composed-architecture scale).

## Reproduction

```bash
pip install -r requirements.txt   # cirq>=1.4, numpy, matplotlib

# Paper 33 — Pentachoric Verification (~30 min)
python paper_33_pvp_19q/cirq/run_p4s_compute_store_cirq.py
python paper_33_pvp_19q/ibm_sim/sim_obs22_pentachoric_ibm.py
python paper_33_pvp_19q/figures/make_paper33_figures.py

# Paper 34 — Ternary spectrum (~3 hours, 324 configs at 28 qubits)
python paper_34_ternary_spectrum_28q/cirq/run_p4s_double_triangle_cirq.py
python paper_34_ternary_spectrum_28q/figures/make_paper34_figures.py
```

RAM: ~2 GB for the 28-qubit state vector. No GPU required. Density-matrix
noise simulation is prohibitive at 28 qubits; Paper 34 is ideal-unitary.

Windows users: set `PYTHONIOENCODING=utf-8` for scripts with Unicode characters.

## Dependencies

- Python 3.13+ (tested on Windows 11)
- Cirq ≥ 1.4
- NumPy, Matplotlib, python-docx
- For Willow hardware deployment: Google Quantum Engine credentials
- For IBM hardware deployment: qiskit-ibm-runtime credentials

## Related repositories

- [`SelinaAliens/tesseract_quantum_implementation`](https://github.com/SelinaAliens/tesseract_quantum_implementation) — primitives this repository composes (Papers 31, 32)
- [`SelinaAliens/The_Merkabit`](https://github.com/SelinaAliens/The_Merkabit) — base-paper companion code
- [`SelinaAliens/merkabit-companion-analysis`](https://github.com/SelinaAliens/merkabit-companion-analysis) — cross-platform KWW / threshold analyses

## License

[MIT](LICENSE) — Copyright © 2026 Selina Stenberg.

## Citation

See [`CITATION.cff`](CITATION.cff). When citing the papers individually, prefer the Zenodo records (DOIs added on release).

## Provenance

Both papers (33, 34) were drafted in collaboration with **Claude (Anthropic, Opus 4.7, 1M-context)** as a coding, analysis, and drafting assistant. The IBM hardware track is co-authored with **Thor Henning Hetland** (Papers 24–26 hardware authorship; the IBM proposal in this repository acknowledges his hardware-track co-authorship). The AI did not execute on IBM or Google hardware and had no operational runtime access; final scientific responsibility rests with the human author.
