"""
Generate Paper 34 figures.

Four figures for the short results paper:
  Fig 1: 28-qubit double-triangle architecture (schematic)
  Fig 2: Entropy spectrum across 36 offsets -- THE central result
  Fig 3: FFT power spectrum -- confirms period-12 + period-6 only
  Fig 4: PSL(2,7) stratum correspondence diagram
         Paper 7 (31 binary -> Riemann zeros)
         Paper 34 (137 ternary -> cyclotomic Z_3)
         open (168 full -> unknown, Observable 25 candidate)
"""
from pathlib import Path
import json
import math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

HERE = Path(__file__).parent.resolve()
STAGE_C_JSON = Path(r"C:/Users/selin/tesseract_quantum_implementation/results/p4s_double_triangle_stageC_20260421T171812.json")

plt.rcParams.update({
    "font.family":        "DejaVu Sans",
    "font.size":          11,
    "figure.dpi":         100,
    "savefig.dpi":        400,
    "savefig.bbox":       "tight",
    "savefig.pad_inches": 0.2,
})

# Load Stage C data
with STAGE_C_JSON.open() as f:
    STAGE_C = json.load(f)


# ---------------------------------------------------------------------------
# FIGURE 1 -- 28-qubit architecture
# ---------------------------------------------------------------------------
def figure_1_architecture():
    fig, ax = plt.subplots(figsize=(11.0, 6.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    ax.text(5.0, 6.55, "28-Qubit Double-Triangle Architecture",
            ha="center", va="center", fontsize=14, fontweight="bold",
            color="#1A1A1A")
    ax.text(5.0, 6.15,
            "Two 137-ternary compute triangles share a single database merkabit",
            ha="center", va="center", fontsize=10, fontstyle="italic",
            color="#555555")

    def draw_triangle(cx, cy, r, color_fill, label, qubit_range):
        ax.add_patch(FancyBboxPatch(
            (cx - r - 0.3, cy - r - 0.5), 2 * r + 0.6, 2 * r + 0.9,
            boxstyle="round,pad=0.04", linewidth=1.1,
            edgecolor="#222222", facecolor=color_fill))
        ax.text(cx, cy + r + 0.25, label, ha="center", va="center",
                 fontsize=11, fontweight="bold")
        a_apex = math.pi / 2
        a_BL   = math.pi / 2 + 2 * math.pi / 3
        a_BR   = math.pi / 2 - 2 * math.pi / 3
        pA = (cx + r * math.cos(a_apex), cy + r * math.sin(a_apex))
        pB = (cx + r * math.cos(a_BL), cy + r * math.sin(a_BL))
        pC = (cx + r * math.cos(a_BR), cy + r * math.sin(a_BR))
        for p0, p1 in [(pA, pB), (pB, pC), (pC, pA)]:
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]],
                     color="#2E5496", linewidth=1.4, zorder=2)
        for (x, y), lab in [(pA, "A"), (pB, "B"), (pC, "C")]:
            ax.add_patch(Circle((x, y), 0.15,
                                 facecolor="white", edgecolor="#222222",
                                 linewidth=1.3, zorder=4))
            ax.text(x, y, lab, ha="center", va="center",
                     fontsize=9, fontweight="bold", zorder=5)
        ax.text(cx, cy - r - 0.3, qubit_range,
                 ha="center", va="center", fontsize=8,
                 fontfamily="monospace", color="#555555")
        return pC  # return C position for memory-tunnel arrow

    # Triangle 1 (left)
    pC1 = draw_triangle(2.4, 3.5, 0.85, "#DCEAF7",
                         "Triangle 1  (T_CYCLE = 12)", "q0\u2013q11")
    # Triangle 2 (right)
    pC2 = draw_triangle(7.6, 3.5, 0.85, "#E6D8F0",
                         "Triangle 2  (T_CYCLE = 12)", "q12\u2013q23")

    # Shared database D in centre
    db_x, db_y = 5.0, 1.4
    ax.add_patch(FancyBboxPatch(
        (db_x - 1.4, db_y - 0.55), 2.8, 1.1,
        boxstyle="round,pad=0.04", linewidth=1.2,
        edgecolor="#222222", facecolor="#F0E6D8"))
    ax.text(db_x, db_y + 0.28, "DATABASE  D  (shared)",
            ha="center", va="center", fontsize=10.5, fontweight="bold")
    ax.text(db_x, db_y - 0.08,
            "u_D stays |0\u27E9   \u00B7   v_D = clock face",
            ha="center", va="center", fontsize=9,
            fontfamily="monospace", color="#444444")
    ax.text(db_x, db_y - 0.38, "q24\u2013q27",
            ha="center", va="center", fontsize=8,
            fontfamily="monospace", color="#555555")

    # Memory tunnels from each triangle's C to shared v_D
    for (pC, col_label) in [(pC1, "u_C1 \u2192 v_D"), (pC2, "u_C2 \u2192 v_D")]:
        arrow = FancyArrowPatch(
            (pC[0] + (0.1 if pC[0] < 5 else -0.1), pC[1] - 0.2),
            (db_x + (-0.7 if pC[0] < 5 else 0.7), db_y + 0.55),
            arrowstyle="->,head_width=3,head_length=5",
            color="#996633", linewidth=2.0,
            connectionstyle="arc3,rad=0.25" if pC[0] < 5 else "arc3,rad=-0.25",
            mutation_scale=8,
        )
        ax.add_patch(arrow)
    ax.text(3.0, 2.25, "u_C1 \u2192 v_D", ha="center", va="center",
             fontsize=8.5, fontfamily="monospace", color="#663300")
    ax.text(7.0, 2.25, "u_C2 \u2192 v_D", ha="center", va="center",
             fontsize=8.5, fontfamily="monospace", color="#663300")
    ax.text(5.0, 3.05, "J_mem = 0.5", ha="center", va="center",
             fontsize=8, fontstyle="italic", color="#663300")

    # Phase-offset annotation
    ax.text(2.4, 4.95, "phase offset = 0",
             ha="center", va="center", fontsize=8.5,
             fontstyle="italic", color="#2E5496")
    ax.text(7.6, 4.95, "phase offset = offset_T2  (swept)",
             ha="center", va="center", fontsize=8.5,
             fontstyle="italic", color="#663399")

    ax.text(5.0, 0.35,
            "Total: 28 qubits   (24 data + 4 database)   \u00B7   "
            "state vector 2\u00B2\u2078 \u00D7 8 B = 2 GB",
            ha="center", va="center", fontsize=9.5,
            color="#222222",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF2C8",
                        edgecolor="#888800", linewidth=1.0))

    out = HERE / "p34_fig1_architecture.png"
    plt.savefig(out, dpi=400, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# FIGURE 2 -- Entropy spectrum (THE central figure)
# ---------------------------------------------------------------------------
def figure_2_entropy_spectrum():
    offsets = STAGE_C["offsets"]
    mean_entropy = [STAGE_C["mean_entropy"][str(o)] for o in offsets]

    fig, ax = plt.subplots(figsize=(12.0, 5.5))

    # Bar chart
    colors = []
    for i, o in enumerate(offsets):
        if o in STAGE_C["collapse_offsets"]:
            colors.append("#CC3333")       # collapse (high entropy) -- red
        elif o in STAGE_C["locking_offsets"]:
            colors.append("#339966")       # locking (low entropy)   -- green
        else:
            colors.append("#999999")       # regular                  -- grey

    bars = ax.bar(offsets, mean_entropy, color=colors,
                   edgecolor="#333333", linewidth=0.5, width=0.8)

    # Period markers: vertical dashed lines at 12, 24
    for x in (12, 24):
        ax.axvline(x - 0.5, color="#555555", linestyle=":", linewidth=1.0,
                    alpha=0.5)

    # Z_3 triadic markers within each period
    for period_start in (0, 12, 24):
        for (triadic, label) in [(4, "T/3"), (8, "2T/3")]:
            x = period_start + triadic
            if x <= 35:
                ax.annotate(f"{label}", xy=(x, 1.165), xytext=(x, 1.17),
                             ha="center", va="bottom", fontsize=8,
                             fontstyle="italic", color="#444444")

    # Reference line at mean entropy
    mean_val = float(np.mean(mean_entropy))
    ax.axhline(mean_val, color="#888888", linewidth=0.8,
                linestyle="--", alpha=0.6)
    ax.text(35, mean_val + 0.001, f"  mean = {mean_val:.4f}",
             ha="right", va="bottom", fontsize=8, color="#666666",
             fontstyle="italic")

    ax.set_xlabel("Phase offset (steps on Coxeter cycle, T_CYCLE = 12)",
                   fontsize=11)
    ax.set_ylabel(r"$\langle S(\rho_{v_D}) \rangle$   "
                   r"(mean von Neumann entropy across 9 label configs)",
                   fontsize=10.5)
    ax.set_title("v$_D$ Entropy Spectrum vs Phase Offset   \u2014   "
                  "Three Coxeter Periods of Offset Sweep",
                  fontsize=12, fontweight="bold")
    ax.set_xlim(-0.8, 35.8)
    ax.set_xticks(list(range(0, 36, 2)))
    ax.set_ylim(1.09, 1.185)
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Legend
    coll_patch  = mpatches.Patch(color="#CC3333", label="collapse  (S max, offset \u2261 4 mod 12)")
    lock_patch  = mpatches.Patch(color="#339966", label="locking   (S min, offset \u2261 8 mod 12)")
    plain_patch = mpatches.Patch(color="#999999", label="regular")
    ax.legend(handles=[coll_patch, lock_patch, plain_patch],
               loc="lower right", fontsize=9, framealpha=0.9)

    # Three-period annotation at top
    for i, (start, end) in enumerate([(0, 11), (12, 23), (24, 35)]):
        ax.annotate(f"Coxeter period {i+1}",
                     xy=((start + end) / 2, 1.183),
                     ha="center", va="top", fontsize=9,
                     fontweight="bold", color="#444444")

    out = HERE / "p34_fig2_entropy_spectrum.png"
    plt.savefig(out, dpi=400, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# FIGURE 3 -- FFT power spectrum
# ---------------------------------------------------------------------------
def figure_3_fft():
    offsets = STAGE_C["offsets"]
    mean_entropy = np.array([STAGE_C["mean_entropy"][str(o)] for o in offsets])

    # FFT on entropy-minus-mean
    fft = np.fft.rfft(mean_entropy - mean_entropy.mean())
    freq = np.fft.rfftfreq(len(mean_entropy), d=1.0)
    power = np.abs(fft) ** 2
    # Period = 1/freq (for freq > 0)

    fig, ax = plt.subplots(figsize=(10.0, 5.5))
    # Plot as stem / bar
    nonzero = freq > 0
    periods = 1.0 / freq[nonzero]
    bar_container = ax.bar(periods, power[nonzero], width=0.25,
                             color="#4477AA", edgecolor="#222222",
                             linewidth=0.8)

    # Annotate the two dominant peaks
    sorted_idx = np.argsort(-power[nonzero])
    for rank, idx in enumerate(sorted_idx[:3]):
        p = periods[idx]
        val = power[nonzero][idx]
        labels = ["fundamental (Coxeter)", "Z\u2082 subharmonic", ""]
        color = ["#CC3333", "#339966", "#888888"][rank]
        ax.annotate(f"T = {p:.2f}\npower = {val:.4f}\n{labels[rank]}",
                     xy=(p, val), xytext=(p + 1.2, val * 0.9),
                     fontsize=9, color=color,
                     arrowprops=dict(arrowstyle="->", color=color, linewidth=1.0))

    # Noise floor annotation
    noise_floor_power = np.mean(power[nonzero][sorted_idx[3:]])
    ax.axhline(noise_floor_power, color="#888888", linestyle="--",
                linewidth=1.0, alpha=0.6)
    ax.text(13.5, noise_floor_power * 1.5,
             f"noise floor  \u2248 {noise_floor_power:.5f}",
             fontsize=8.5, color="#666666", fontstyle="italic")

    ax.set_xlabel("Period (offset steps)", fontsize=11)
    ax.set_ylabel("Power  |FFT(S - \u27E8S\u27E9)|\u00B2", fontsize=11)
    ax.set_title("FFT of the Entropy Spectrum   \u2014   "
                  "Two Dominant Components, Rest at Noise Floor",
                  fontsize=12, fontweight="bold")
    ax.set_yscale("log")
    ax.set_ylim(1e-6, 0.2)
    ax.set_xlim(0, 20)
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    out = HERE / "p34_fig3_fft.png"
    plt.savefig(out, dpi=400, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# FIGURE 4 -- PSL(2,7) stratum correspondence
# ---------------------------------------------------------------------------
def figure_4_stratum_correspondence():
    fig, ax = plt.subplots(figsize=(11.0, 6.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    ax.text(5.0, 6.55,
            "The Spectrum of Zeros at Each PSL(2,7) Stratum",
            ha="center", va="center", fontsize=13.5, fontweight="bold",
            color="#1A1A1A")
    ax.text(5.0, 6.15,
            "168 = 31 (binary matter) + 62 (weak boundary) + 75 (confined) "
            "\u2014 each stratum has its own spectrum",
            ha="center", va="center", fontsize=10, fontstyle="italic",
            color="#555555")

    # Three boxes
    box_h = 4.1
    box_specs = [
        (0.4, 1.5, 2.9, box_h, "#DCEAF7", "#2E5496",
          "31  BINARY",
          "Single rotating triangle",
          "No F, no P  (no standing wave)",
          "Gates: {R, S, T}",
          "Operator:  truncated\nDirichlet series Z(s)",
          "SPECTRUM:\nRiemann zeros",
          "Paper 7\n(Analysis 39: 29/29\nzeros confirmed)",
          "#CC3333"),
        (3.55, 1.5, 2.9, box_h, "#F0E6D8", "#663300",
          "137  TERNARY",
          "Two coupled compute triangles",
          "Full  {R, S, T, F, P}  per merkabit",
          "Shared substrate (database v_D)",
          "Operator:  coupled-triangle\ntransfer matrix",
          "SPECTRUM:\ncyclotomic Z\u2083",
          "Paper 34 (this paper)\nStage C: 36-offset\nsweep confirms",
          "#CC3333"),
        (6.7, 1.5, 2.9, box_h, "#E6D8F0", "#663399",
          "168  FULL",
          "Full PSL(2,7) action",
          "31 \u2297 62 \u2297 75  coupled",
          "B\u2083\u2081 + Z\u2086\u2082 + T\u2087\u2085 together",
          "Operator:  unknown\n(open)",
          "SPECTRUM:\nunknown",
          "Open\n(Observable 25\ncandidate)",
          "#AAAAAA"),
    ]

    for (x, y, w, h, fc, ec, title, sub1, sub2, sub3, op, spec, status, status_col) in box_specs:
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.04",
            linewidth=1.4, edgecolor=ec, facecolor=fc))

        # Title band
        cy_title = y + h - 0.25
        ax.text(x + w / 2, cy_title, title,
                ha="center", va="center", fontsize=12, fontweight="bold",
                color="#1A1A1A")
        # Subtitle items
        y_cursor = cy_title - 0.45
        for line in [sub1, sub2, sub3]:
            ax.text(x + w / 2, y_cursor, line,
                    ha="center", va="center", fontsize=8.5,
                    color="#333333")
            y_cursor -= 0.3

        # Operator
        y_cursor -= 0.15
        for line in op.split("\n"):
            ax.text(x + w / 2, y_cursor, line,
                    ha="center", va="center", fontsize=8.5,
                    fontstyle="italic", color="#444444")
            y_cursor -= 0.25

        # Spectrum (big highlight)
        y_cursor -= 0.15
        for line in spec.split("\n"):
            ax.text(x + w / 2, y_cursor, line,
                    ha="center", va="center", fontsize=10.5,
                    fontweight="bold", color=status_col)
            y_cursor -= 0.30

        # Status
        y_cursor -= 0.15
        for line in status.split("\n"):
            ax.text(x + w / 2, y_cursor, line,
                    ha="center", va="center", fontsize=8.5,
                    fontstyle="italic", color="#555555")
            y_cursor -= 0.22

    # Footer explaining correspondence
    ax.text(5.0, 0.9,
            "Paper 7 establishes the binary (31) spectrum.  "
            "Paper 34 establishes the ternary (137) spectrum.",
            ha="center", va="center", fontsize=10,
            color="#222222")
    ax.text(5.0, 0.55,
            "Both strata emerge from the same PSL(2,7) decomposition; "
            "their spectra are complementary halves of one structure.",
            ha="center", va="center", fontsize=9.5,
            fontstyle="italic", color="#555555")
    ax.text(5.0, 0.2,
            "Observable 24 (forthcoming): incommensurate 137 \u00D7 137 coupling "
            "\u2014 Paper 7 Regime 3 \u2014 GUE-like predicted.",
            ha="center", va="center", fontsize=9.5,
            fontstyle="italic", color="#663399")

    out = HERE / "p34_fig4_stratum_correspondence.png"
    plt.savefig(out, dpi=400, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


if __name__ == "__main__":
    figure_1_architecture()
    figure_2_entropy_spectrum()
    figure_3_fft()
    figure_4_stratum_correspondence()
    print("\nAll 4 figures generated.")
