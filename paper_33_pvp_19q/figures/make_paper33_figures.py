"""
Generate Paper 35 v2 figures (tesseract-only, no octonion layer).

5 figures:
  Fig 1: The closed loop -- write / compute / store / read / clock
  Fig 2: 19-qubit architecture layout (compute triangle + database + reference + ancilla)
  Fig 3: Z_3 cyclic clock -- alpha -> gamma -> beta -> alpha
  Fig 4: Five pentachoric gates mapped to stages 1-5
  Fig 5: Cross-platform simulation results (cycled gap across Cirq ideal / Heron / Eagle)
"""
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

HERE = Path(__file__).parent.resolve()

plt.rcParams.update({
    "font.family":        "DejaVu Sans",
    "font.size":          11,
    "axes.linewidth":     0.8,
    "axes.edgecolor":     "#333333",
    "figure.dpi":         100,
    "savefig.dpi":        300,
    "savefig.bbox":       "tight",
    "savefig.pad_inches": 0.15,
})

# Color palette
C_COMPUTE = "#DCEAF7"   # soft blue
C_MEMORY  = "#F0E6D8"   # warm cream
C_DB      = "#E6D8F0"   # soft purple
C_REF     = "#E6F0DC"   # soft green
C_ANC     = "#F0DCDC"   # soft red
C_EDGE    = "#2E5496"   # navy for edges/arrows
C_ACCENT  = "#FFF2C8"   # highlight yellow


# ============================================================================
# Figure 1 -- The closed computational loop
# ============================================================================
def figure_1_closed_loop():
    fig, ax = plt.subplots(figsize=(10.5, 7.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Title
    ax.text(5.0, 9.55, "The Closed Computational Loop",
            ha="center", va="center", fontsize=14, fontweight="bold",
            color="#222222")
    ax.text(5.0, 9.05,
            "Write \u2192 Compute \u2192 Store \u2192 Read \u2192 Clock  \u2014  "
            "all native, no external gates",
            ha="center", va="center", fontsize=10.5, fontstyle="italic",
            color="#555555")

    # WRITE node (left)
    ax.add_patch(FancyBboxPatch(
        (0.3, 5.8), 2.0, 1.6, boxstyle="round,pad=0.04",
        linewidth=1.2, edgecolor="#333333", facecolor=C_REF))
    ax.text(1.3, 6.8, "WRITE", ha="center", va="center",
             fontsize=11.5, fontweight="bold")
    ax.text(1.3, 6.4, "Z\u2083 eigenstate\nstate_prep_2q",
             ha="center", va="center", fontsize=9.5)
    ax.text(1.3, 5.55, "Paper 32", ha="center", va="center",
             fontsize=8.5, fontstyle="italic", color="#555555")

    # COMPUTE (center, bigger box with triangle inside)
    ax.add_patch(FancyBboxPatch(
        (3.2, 5.2), 3.6, 3.0, boxstyle="round,pad=0.04",
        linewidth=1.2, edgecolor="#333333", facecolor=C_COMPUTE))
    ax.text(5.0, 7.85, "COMPUTE TRIANGLE",
             ha="center", va="center", fontsize=11.5, fontweight="bold")
    # Draw a small triangle inside
    tri_cx, tri_cy = 5.0, 6.4
    tri_r = 0.85
    pts = [
        (tri_cx, tri_cy + tri_r),        # A (top)
        (tri_cx - tri_r * 0.866, tri_cy - tri_r * 0.5),  # B (lower-left)
        (tri_cx + tri_r * 0.866, tri_cy - tri_r * 0.5),  # C (lower-right)
    ]
    for i in range(3):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % 3]
        ax.plot([x0, x1], [y0, y1], color=C_EDGE, linewidth=1.8)
    labels = ["A", "B", "C"]
    for (x, y), lab in zip(pts, labels):
        ax.plot(x, y, "o", markersize=18, color="white",
                 markeredgewidth=1.5, markeredgecolor="#222222")
        ax.text(x, y, lab, ha="center", va="center",
                 fontsize=10, fontweight="bold", color="#222222")
    ax.text(5.0, 5.45, "Paper 32  \u00B7  J_intra = 0.1",
             ha="center", va="center", fontsize=8.5, fontstyle="italic",
             color="#555555")

    # STORE (right) -- moved further right to create room for tunnel labels
    ax.add_patch(FancyBboxPatch(
        (8.2, 5.45), 1.6, 2.05, boxstyle="round,pad=0.04",
        linewidth=1.2, edgecolor="#333333", facecolor=C_DB))
    ax.text(9.0, 7.2, "STORE", ha="center", va="center",
             fontsize=11.5, fontweight="bold")
    ax.text(9.0, 6.75, "Database D",
             ha="center", va="center", fontsize=9.5)
    ax.text(9.0, 6.35, "u_D stays |0\u27E9",
             ha="center", va="center", fontsize=8.5)
    ax.text(9.0, 6.02, "v_D = content",
             ha="center", va="center", fontsize=8.5)
    ax.text(9.0, 5.6, "Paper 31", ha="center", va="center",
             fontsize=8, fontstyle="italic", color="#555555")

    # READ (bottom-right of STORE, aligned to new STORE x position)
    ax.add_patch(FancyBboxPatch(
        (8.2, 2.8), 1.6, 1.6, boxstyle="round,pad=0.04",
        linewidth=1.2, edgecolor="#333333", facecolor=C_ANC))
    ax.text(9.0, 3.8, "READ", ha="center", va="center",
             fontsize=11.5, fontweight="bold")
    ax.text(9.0, 3.4,
             "SWAP test\nvs Z\u2083 reference",
             ha="center", va="center", fontsize=9)
    ax.text(9.0, 2.55, "Paper 18", ha="center", va="center",
             fontsize=8, fontstyle="italic", color="#555555")

    # Arrows between boxes
    # WRITE -> COMPUTE
    ax.annotate("", xy=(3.15, 6.6), xytext=(2.35, 6.6),
                 arrowprops=dict(arrowstyle="->", color=C_EDGE, linewidth=1.8))
    ax.text(2.75, 6.9, "Z\u2083 label", ha="center", va="center",
             fontsize=8.5, fontstyle="italic", color="#444444")

    # COMPUTE -> STORE (memory tunnel). Two short labels, carefully placed.
    ax.annotate("", xy=(8.15, 6.6), xytext=(6.85, 6.6),
                 arrowprops=dict(arrowstyle="->", color=C_EDGE, linewidth=2.0))
    ax.text(7.5, 6.95, "memory tunnel  (J=0.5)",
             ha="center", va="bottom", fontsize=8,
             fontstyle="italic", color="#444444")
    ax.text(7.5, 6.32, "u_C \u2192 v_D",
             ha="center", va="top", fontsize=8,
             fontfamily="monospace", color="#555555")

    # STORE -> READ (arrow now at x=9.0 to match new box position)
    ax.annotate("", xy=(9.0, 4.45), xytext=(9.0, 5.4),
                 arrowprops=dict(arrowstyle="->", color=C_EDGE, linewidth=1.8))

    # READ -> loop-back arrow (Z_3 clock tick returns to WRITE)
    ax.annotate("", xy=(2.3, 5.8), xytext=(8.15, 3.6),
                 arrowprops=dict(arrowstyle="->", color="#996699",
                                   linewidth=1.8,
                                   connectionstyle="arc3,rad=-0.3"))
    ax.text(4.5, 3.0, "Z\u2083 CLOCK: three cycles return to \u03B1",
             ha="center", va="center", fontsize=10,
             fontweight="bold", color="#663366",
             bbox=dict(boxstyle="round,pad=0.3", facecolor=C_ACCENT,
                        edgecolor="#996699", linewidth=1.1))

    # Footer tagline
    ax.text(5.0, 1.15,
            "Every operation: same cross-chiral tunnel primitive at a different coupling strength.",
            ha="center", va="center", fontsize=10, fontstyle="italic",
            color="#333333")
    ax.text(5.0, 0.75,
            "No external gates. No octonion layer. 19 qubits total.",
            ha="center", va="center", fontsize=10, fontweight="bold",
            color="#222222")

    out = HERE / "p33_fig1_closed_loop.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


# ============================================================================
# Figure 2 -- 19-qubit architecture layout
# ============================================================================
def figure_2_architecture():
    fig, ax = plt.subplots(figsize=(10.5, 7.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Title
    ax.text(5.0, 9.55, "19-Qubit Architecture Layout",
            ha="center", va="center", fontsize=14, fontweight="bold",
            color="#222222")
    ax.text(5.0, 9.05,
            "Qubit allocation across the four registers + ancilla",
            ha="center", va="center", fontsize=10, fontstyle="italic",
            color="#555555")

    # Three compute-triangle merkabits A, B, C
    tri_cx, tri_cy = 2.7, 5.8
    tri_r = 1.7
    merkabit_positions = [
        ("A", tri_cx, tri_cy + tri_r),
        ("B", tri_cx - tri_r * 0.866, tri_cy - tri_r * 0.55),
        ("C", tri_cx + tri_r * 0.866, tri_cy - tri_r * 0.55),
    ]
    # Triangle edges
    for i in range(3):
        _, x0, y0 = merkabit_positions[i]
        _, x1, y1 = merkabit_positions[(i + 1) % 3]
        ax.plot([x0, x1], [y0, y1], color=C_EDGE, linewidth=1.3,
                 linestyle="--", alpha=0.6)

    # Draw each merkabit as a box with u_x and v_x sub-boxes
    def draw_merkabit(name, cx, cy, u_qubits, v_qubits, facecol):
        w, h = 1.1, 1.1
        ax.add_patch(FancyBboxPatch(
            (cx - w / 2, cy - h / 2), w, h,
            boxstyle="round,pad=0.02",
            linewidth=1.1, edgecolor="#333333", facecolor=facecol))
        ax.text(cx, cy + 0.32, name, ha="center", va="center",
                 fontsize=10.5, fontweight="bold")
        ax.text(cx, cy + 0.05, f"u: q[{u_qubits[0]},{u_qubits[1]}]",
                 ha="center", va="center", fontsize=8,
                 fontfamily="monospace")
        ax.text(cx, cy - 0.17, f"v: q[{v_qubits[0]},{v_qubits[1]}]",
                 ha="center", va="center", fontsize=8,
                 fontfamily="monospace")
        ax.text(cx, cy - 0.42, "4 qubits", ha="center", va="center",
                 fontsize=7.5, fontstyle="italic", color="#555555")

    # A: q0-q3, B: q4-q7, C: q8-q11
    for (name, x, y), (uq, vq), col in zip(
        merkabit_positions,
        [((0, 1), (2, 3)), ((4, 5), (6, 7)), ((8, 9), (10, 11))],
        [C_COMPUTE, C_COMPUTE, C_COMPUTE],
    ):
        draw_merkabit(name, x, y, uq, vq, col)

    # Compute triangle frame label
    ax.text(tri_cx, 2.4, "COMPUTE TRIANGLE",
            ha="center", va="center", fontsize=10.5, fontweight="bold")
    ax.text(tri_cx, 2.05, "12 qubits \u00B7 3 merkabits \u00B7 J_intra = 0.1",
            ha="center", va="center", fontsize=8.5, fontstyle="italic",
            color="#555555")
    # Triangle bounding region (subtle)
    ax.add_patch(FancyBboxPatch(
        (0.2, 2.7), 5.0, 5.3, boxstyle="round,pad=0.05",
        linewidth=0.8, edgecolor="#888888", facecolor="none",
        linestyle="--", alpha=0.5))

    # Memory tunnel arrow from C (right of triangle) to D.
    # Use a curved arc that sweeps above the straight line so the label sits
    # clearly above both endpoints.
    c_name, c_x, c_y = merkabit_positions[2]
    d_cx, d_cy = 7.3, 5.1
    ax.annotate("", xy=(d_cx - 0.55, d_cy + 0.2),
                 xytext=(c_x + 0.55, c_y + 0.2),
                 arrowprops=dict(arrowstyle="->", color="#996633",
                                   linewidth=2.0,
                                   connectionstyle="arc3,rad=-0.25"))
    # Label ABOVE the arc, well clear of both boxes.
    ax.text(5.95, 6.95, "memory tunnel", ha="center", va="center",
             fontsize=9.5, fontweight="bold", color="#663300")
    ax.text(5.95, 6.55, "u_C \u2192 v_D   J_mem = 0.5",
             ha="center", va="center", fontsize=8,
             fontfamily="monospace", color="#663300")

    # Database D
    draw_merkabit("D", d_cx, d_cy, (12, 13), (14, 15), C_DB)
    ax.text(d_cx, d_cy - 0.85, "DATABASE", ha="center", va="center",
             fontsize=10, fontweight="bold", color="#333333")
    ax.text(d_cx, d_cy - 1.15,
             "u_D stays |0\u27E9  \u00B7  v_D = stored content",
             ha="center", va="center", fontsize=8, color="#555555")

    # Reference register (right side)
    ax.add_patch(FancyBboxPatch(
        (8.6, 6.3), 1.2, 1.3, boxstyle="round,pad=0.02",
        linewidth=1.1, edgecolor="#333333", facecolor=C_REF))
    ax.text(9.2, 7.3, "REFERENCE", ha="center", va="center",
             fontsize=9.5, fontweight="bold")
    ax.text(9.2, 6.95, "ref: q[16,17]",
             ha="center", va="center", fontsize=8,
             fontfamily="monospace")
    ax.text(9.2, 6.65, "Z\u2083 eigenstate",
             ha="center", va="center", fontsize=7.5,
             fontstyle="italic", color="#555555")
    ax.text(9.2, 6.4, "2 qubits", ha="center", va="center",
             fontsize=7.5, color="#555555")

    # Ancilla
    ax.add_patch(FancyBboxPatch(
        (8.6, 4.6), 1.2, 1.1, boxstyle="round,pad=0.02",
        linewidth=1.1, edgecolor="#333333", facecolor=C_ANC))
    ax.text(9.2, 5.4, "ANCILLA", ha="center", va="center",
             fontsize=9.5, fontweight="bold")
    ax.text(9.2, 5.1, "anc: q[18]",
             ha="center", va="center", fontsize=8,
             fontfamily="monospace")
    ax.text(9.2, 4.8, "SWAP test", ha="center", va="center",
             fontsize=7.5, fontstyle="italic", color="#555555")

    # SWAP test connection from D to ref via ancilla
    ax.annotate("", xy=(8.55, 6.8), xytext=(d_cx + 0.55, d_cy + 0.2),
                 arrowprops=dict(arrowstyle="->", color="#339966",
                                   linewidth=1.4,
                                   connectionstyle="arc3,rad=0.2"))
    ax.text(8.25, 5.95, "SWAP", ha="center", va="center",
             fontsize=8, color="#226644")

    # Total qubit count footer
    ax.text(5.0, 0.8,
            "Total:  12 (triangle) + 4 (database) + 2 (reference) + 1 (ancilla)  =  19 qubits",
            ha="center", va="center", fontsize=10.5, fontweight="bold",
            color="#222222",
            bbox=dict(boxstyle="round,pad=0.4", facecolor=C_ACCENT,
                        edgecolor="#888800", linewidth=1.0))

    out = HERE / "p33_fig2_architecture.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


# ============================================================================
# Figure 3 -- Z_3 cyclic clock
# ============================================================================
def figure_3_z3_clock():
    fig, ax = plt.subplots(figsize=(9.0, 7.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Title
    ax.text(5.0, 9.45, "The Z\u2083 Cyclic Clock",
            ha="center", va="center", fontsize=14, fontweight="bold",
            color="#222222")
    ax.text(5.0, 9.0,
            "Native computation: \u03B1 \u2192 \u03B3 \u2192 \u03B2 \u2192 \u03B1. Three writes return to start.",
            ha="center", va="center", fontsize=10.5, fontstyle="italic",
            color="#555555")

    # Three label nodes arranged in a clockwise triangle
    cx, cy, r = 5.0, 5.0, 2.5
    import math
    angles = [math.pi / 2, math.pi / 2 - 2 * math.pi / 3, math.pi / 2 + 2 * math.pi / 3]
    labels = ["\u03B1\nalpha", "\u03B3\ngamma", "\u03B2\nbeta"]
    label_keys = ["alpha", "gamma", "beta"]
    colors = ["#DCEAF7", "#E6F0DC", "#F0E6D8"]  # soft blue, green, cream

    positions = []
    for a, lab, key, col in zip(angles, labels, label_keys, colors):
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        positions.append((x, y, lab, key, col))
        ax.add_patch(Circle((x, y), 0.85, linewidth=1.4,
                             edgecolor="#333333", facecolor=col, zorder=3))
        ax.text(x, y, lab, ha="center", va="center",
                 fontsize=13, fontweight="bold", zorder=4)

    # Arrows between nodes (cyclic: alpha -> gamma -> beta -> alpha)
    arrow_labels = [
        ("write \u03B1, read \u03B3", "\u03B1 \u2192 \u03B3"),
        ("write \u03B3, read \u03B2", "\u03B3 \u2192 \u03B2"),
        ("write \u03B2, read \u03B1", "\u03B2 \u2192 \u03B1"),
    ]
    for i in range(3):
        x0, y0, _, _, _ = positions[i]
        x1, y1, _, _, _ = positions[(i + 1) % 3]
        dx, dy = x1 - x0, y1 - y0
        import math as _m
        L = _m.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        # Start/end points shrunk so arrows don't overlap the circles
        sx, sy = x0 + 0.85 * ux, y0 + 0.85 * uy
        ex, ey = x1 - 0.85 * ux, y1 - 0.85 * uy
        ax.annotate("", xy=(ex, ey), xytext=(sx, sy),
                     arrowprops=dict(arrowstyle="->", color="#663399",
                                       linewidth=2.4,
                                       connectionstyle="arc3,rad=0.2"))
        # Label the transition
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        # Offset label outside the triangle
        nx, ny = -uy, ux
        lx, ly = mx + nx * 0.5, my + ny * 0.5
        prose, short = arrow_labels[i]
        ax.text(lx, ly, short, ha="center", va="center",
                 fontsize=11, fontweight="bold", color="#663399",
                 bbox=dict(boxstyle="round,pad=0.2",
                             facecolor="white", edgecolor="#663399",
                             linewidth=0.8))

    # Center annotation
    ax.text(cx, cy, "3 ticks = 1 period",
            ha="center", va="center", fontsize=10,
            fontstyle="italic", color="#663399",
            bbox=dict(boxstyle="round,pad=0.25", facecolor=C_ACCENT,
                        edgecolor="#888800", linewidth=1.0))

    # Footer
    ax.text(5.0, 1.6,
            "The Z\u2083 rotation was not programmed \u2014 it emerged from composing",
            ha="center", va="center", fontsize=10, color="#333333")
    ax.text(5.0, 1.2,
            "three triangle-edge tunnels with one memory tunnel.",
            ha="center", va="center", fontsize=10, color="#333333")
    ax.text(5.0, 0.65,
            "A Z\u2083-symmetric substrate natively performs Z\u2083 arithmetic.",
            ha="center", va="center", fontsize=10.5, fontweight="bold",
            color="#222222")

    out = HERE / "p33_fig3_z3_clock.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


# ============================================================================
# Figure 4 -- Five pentachoric stages mapped to gates
# ============================================================================
def figure_4_five_stages():
    fig, ax = plt.subplots(figsize=(11.0, 7.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Title
    ax.text(5.0, 9.55,
            "The Pentachoric Verification Protocol: Five Gates, Five Stages",
            ha="center", va="center", fontsize=13.5, fontweight="bold",
            color="#222222")
    ax.text(5.0, 9.1,
            "Each stage tests one architectural primitive corresponding to one gate of Paper 24's ouroboros cycle.",
            ha="center", va="center", fontsize=10, fontstyle="italic",
            color="#555555")

    # Header band
    header_y = 8.35
    ax.add_patch(FancyBboxPatch(
        (0.4, header_y - 0.3), 9.2, 0.65,
        boxstyle="round,pad=0.02", linewidth=0.8,
        edgecolor="#333333", facecolor="#2E5496"))
    hx = [0.8, 1.8, 3.8, 7.0]
    hlabels = ["GATE", "NAME", "STAGE TEST", "PASS THRESHOLD"]
    for x, h in zip(hx, hlabels):
        ax.text(x, header_y, h, ha="left", va="center",
                 fontsize=9.5, fontweight="bold", color="white")

    # Rows (gate, name, description, threshold, colour)
    rows = [
        ("S", "Substrate",
          "Run compute triangle alone.\nMeasure \u27E8u|v\u27E9 on A, B, C.",
          "mean |\u27E8u|v\u27E9| \u2208 [0.30, 0.65]",
          "#DCEAF7"),
        ("R", "Rotation",
          "3 \u00D7 3 write-read at J_mem = 0.5.\nCycled-diagonal gap of \u03B1\u2192\u03B3, \u03B2\u2192\u03B1, \u03B3\u2192\u03B2.",
          "cycled gap \u2265 +0.08  at  \u03C3 \u2265 2.0",
          "#F0E6D8"),
        ("T", "Transfer",
          "Null control: same as R but\nwithout the memory tunnel.",
          "|cycled gap| \u2264 0.03",
          "#E6D8F0"),
        ("F", "Frequency",
          "Sweep J_mem \u2208 {0, 0.25, 0.5, 0.75, 1.0}.\nFind peak-gap coupling.",
          "peak  J_mem \u2208 (0.30, 0.70)",
          "#E6F0DC"),
        ("P", "Phase",
          "Read u_D directly (not v_D).\nCheck cross-chirality rule.",
          "|u_D gap| \u2264 0.03",
          "#F0DCDC"),
    ]
    row_ys = [7.3, 6.05, 4.8, 3.55, 2.3]
    for (gate, name, test, thresh, col), y in zip(rows, row_ys):
        ax.add_patch(FancyBboxPatch(
            (0.4, y - 0.52), 9.2, 1.08,
            boxstyle="round,pad=0.02", linewidth=0.7,
            edgecolor="#555555", facecolor=col))
        # Gate letter (big)
        ax.add_patch(Circle((0.9, y), 0.32, linewidth=1.3,
                             edgecolor="#333333", facecolor="white"))
        ax.text(0.9, y, gate, ha="center", va="center",
                 fontsize=15, fontweight="bold", color="#222222")
        # Name
        ax.text(1.8, y + 0.02, name, ha="left", va="center",
                 fontsize=11, fontweight="bold")
        # Stage test description
        ax.text(3.8, y + 0.02, test, ha="left", va="center",
                 fontsize=9.5, color="#222222")
        # Threshold
        ax.text(7.0, y + 0.02, thresh, ha="left", va="center",
                 fontsize=10, fontfamily="monospace", color="#222222")

    # Footer
    ax.text(5.0, 1.3,
            "STRONG PASS = all five gates pass  \u00B7  WEAK PASS = S + R + P pass  \u00B7  NULL = R fails",
            ha="center", va="center", fontsize=10, fontweight="bold",
            color="#222222",
            bbox=dict(boxstyle="round,pad=0.35", facecolor=C_ACCENT,
                        edgecolor="#888800", linewidth=1.0))
    ax.text(5.0, 0.65,
            "Decisive test: Stage R.  If the Z\u2083 cyclic shift \u03B1\u2192\u03B3\u2192\u03B2 does not emerge, primitive-completeness is falsified.",
            ha="center", va="center", fontsize=9.5, fontstyle="italic",
            color="#555555")

    out = HERE / "p33_fig4_five_stages.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


# ============================================================================
# Figure 5 -- Cross-platform simulation results
# ============================================================================
def figure_5_cross_platform():
    import numpy as np
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.5),
                              gridspec_kw={"width_ratios": [1.2, 1]})

    # LEFT: bar chart of cycled gap by platform
    ax1 = axes[0]
    platforms = ["Cirq ideal\n(p = 0)",
                  "IBM Heron r2\n(p = 0.003)",
                  "IBM Eagle r3\n(p = 0.005)"]
    gaps    = [0.159, 0.110, 0.086]
    errs    = [0.07,  0.031, 0.028]
    sigmas  = [2.3,   3.56,  3.06]
    colors  = ["#DCEAF7", "#F0E6D8", "#F0DCDC"]

    x = np.arange(len(platforms))
    bars = ax1.bar(x, gaps, yerr=errs, capsize=8,
                    color=colors, edgecolor="#333333", linewidth=1.1)
    # Threshold line
    ax1.axhline(0.08, color="#CC3333", linestyle="--", linewidth=1.4)
    ax1.text(2.45, 0.083, "pre-registration threshold (+0.08)",
              ha="right", va="bottom", fontsize=8.5,
              fontstyle="italic", color="#CC3333")
    # Annotate sigmas on bars
    for i, (g, e, s) in enumerate(zip(gaps, errs, sigmas)):
        ax1.text(i, g + e + 0.008, f"+{s:.2f}\u03C3",
                  ha="center", va="bottom", fontsize=10,
                  fontweight="bold", color="#222222")
        ax1.text(i, g / 2, f"+{g:.3f}",
                  ha="center", va="center", fontsize=10,
                  fontweight="bold", color="#222222")

    ax1.set_xticks(x)
    ax1.set_xticklabels(platforms, fontsize=9.5)
    ax1.set_ylabel("Cycled-diagonal gap (Stage R)", fontsize=10.5)
    ax1.set_title("Z\u2083 rotation signal across three noise profiles",
                   fontsize=11, fontweight="bold")
    ax1.set_ylim(0, 0.28)
    ax1.grid(True, axis="y", linestyle=":", alpha=0.5)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # RIGHT: pass/fail matrix of all five gates across platforms
    ax2 = axes[1]
    gate_names = ["S", "R", "T", "F", "P"]
    platform_labels = ["Ideal", "Heron r2", "Eagle r3"]
    # Pass/fail: all 5 pass on ideal; 5/5 on Heron (F structural); 4/5 on Eagle (F skipped)
    results = [
        ["PASS", "PASS", "PASS", "PASS", "PASS"],   # Ideal
        ["PASS", "PASS", "PASS", "\u25CB", "PASS"], # Heron -- F structural
        ["PASS", "PASS", "PASS", "\u25CB", "PASS"], # Eagle -- F skipped
    ]
    ax2.set_xlim(-0.5, len(gate_names) - 0.5)
    ax2.set_ylim(-0.5, len(platform_labels) - 0.5)
    for i, platform in enumerate(platform_labels):
        for j, gate in enumerate(gate_names):
            result = results[i][j]
            color = "#4CAF50" if result == "PASS" else "#BDBDBD"
            ax2.add_patch(mpatches.Rectangle(
                (j - 0.45, i - 0.45), 0.9, 0.9,
                facecolor=color, edgecolor="#333333", linewidth=1.0))
            if result == "PASS":
                ax2.text(j, i, "\u2713", ha="center", va="center",
                         fontsize=22, fontweight="bold", color="white")
            else:
                ax2.text(j, i, "\u2014", ha="center", va="center",
                         fontsize=18, color="#666666")
    ax2.set_xticks(range(len(gate_names)))
    ax2.set_xticklabels(gate_names, fontsize=14, fontweight="bold")
    ax2.set_yticks(range(len(platform_labels)))
    ax2.set_yticklabels(platform_labels, fontsize=10.5)
    ax2.set_title("Pentachoric gates across platforms",
                   fontsize=11, fontweight="bold")
    ax2.invert_yaxis()
    for spine in ax2.spines.values():
        spine.set_visible(False)
    ax2.tick_params(length=0)

    # Legend: gray squares = F gate structural-pass (argmax needs more trials)
    ax2.text(2.0, 3.25,
             "\u2713 pass at pre-registered threshold  \u00B7  \u2014 F-sweep argmax statistical (needs n_trials \u2265 10)",
             ha="center", va="center", fontsize=8.5, fontstyle="italic",
             color="#555555")

    plt.suptitle("Cross-Platform Simulation Results for the Pentachoric Verification Protocol",
                  fontsize=12.5, fontweight="bold", y=1.02)

    out = HERE / "p33_fig5_cross_platform.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out}")


if __name__ == "__main__":
    figure_1_closed_loop()
    figure_2_architecture()
    figure_3_z3_clock()
    figure_4_five_stages()
    figure_5_cross_platform()
    print("\nAll 5 figures generated.")
