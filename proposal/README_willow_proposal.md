# Pentachoric Verification Protocol

**A falsifiable hardware test for whether the merkabit architecture is a primitive-complete, self-hosting quantum computer.**

Five pentachoric gates, one 19-qubit circuit, five independent pass/fail thresholds. If all five gates pass on Google Willow hardware, the merkabit's write-compute-store-read-clock loop is operational end-to-end — the architecture that derives α = 1/137.036 from E₆ Coxeter geometry also runs a working quantum computer on 19 qubits.

## What this repo contains

| File | Purpose |
|---|---|
| `PROPOSAL.md` | Willow Early Access proposal (markdown source) |
| `build_proposal.js` | DOCX generator for the proposal |
| `PREDICTION.md` | Pre-registered pass/fail thresholds for Observables 14, 16, 17, 22 |

The initial commit of `PREDICTION.md` is the **timestamped pre-registration anchor**. Any later hardware result can be compared against thresholds that were locked in before any Google hardware access.

## The claim

The merkabit framework (Papers 1–28) derives the universe's constants from E₆ geometry and the PSL(2,7) decomposition with zero free parameters. Papers 24–26 confirmed 5/5 hardware predictions on IBM Eagle r3 and Heron r2. Papers 31–35 compose the primitives into a quantum computing stack and demonstrate in simulation that the composition closes as a **native Z₃ cyclic clock**: writing label X produces a stored state recognising cycle(X) = X⁻¹ under the Z₃ Galois group. Three writes return to the original label.

The Pentachoric Verification Protocol tests whether that closure survives on hardware. Five stages, each isolating one of the five gates of the ouroboros cycle:

| Gate | Name | Tests |
|---|---|---|
| **S** | Substrate | Does the compute triangle self-sustain? |
| **R** | Rotation | Does the pipeline rotate labels in Z₃? |
| **T** | Transfer | Is the tunnel the content-routing operator? |
| **F** | Frequency | What's the optimal memory-write coupling? |
| **P** | Phase | Is the u/v cross-chirality rule preserved? |

All five must pass for the **STRONG PASS** verdict. Any single failure falsifies one specific named primitive.

## Companion repositories

- **`selinaserephina-star/tesseract_quantum_implementation`** — Cirq circuit builders and Willow submission scripts (`willow/obs14_tunnel.py`, `willow/obs16_triangle.py`, `willow/obs17_square.py`, `willow/obs22_pentachoric.py`). The scripts pre-date the hardware submission and are the authoritative source for the protocol.
- **`selinaserephina-star/willow_hardware_merkabit`** — Phase 1 Willow proposal (*Cross-Architecture Test of Geometric Anti-Bunching*, March 2026). Phase 1 tested a single primitive; this repo tests the full compose.
- **`selinaserephina-star/merkabit_hardware_test`** — IBM Eagle r3 and Heron r2 hardware track record (Papers 24–26).

## Reproducibility

The Cirq simulation smoke-test of Observable 22 (19 qubits, n_trials=2, shots=256 — deliberately underpowered) already returns **STRONG PASS on all five gates**. The full simulation at n_trials=10, shots=2048 reports cycled-diagonal gap = +0.159 ± 0.07 (+2.3σ). See `PROPOSAL.md` §3.5 for details.

To reproduce the sim:

```bash
git clone https://github.com/selinaserephina-star/tesseract_quantum_implementation.git
cd tesseract_quantum_implementation/willow
python obs22_pentachoric.py --sim-only --n-trials 10 --shots 2048
```

## Authors

- Selina Stenberg (principal)
- Claude (Anthropic, Opus 4.7 1M-context) — AI collaborator for simulation, analysis, and manuscript drafting
- Thor Henning Hetland (IBM hardware track, Papers 24–26)

Final scientific responsibility rests with the human author.

## License

Not yet licensed. A public-facing mirror at `github.com/SelinaAliens/pentachoric_verification_protocol` will be activated with an MIT license when Paper 35 posts to Zenodo.
