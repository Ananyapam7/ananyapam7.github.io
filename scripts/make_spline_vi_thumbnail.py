"""Generate the minimal Spline VI blog thumbnail from normalized cubic B-splines.

Run: MPLCONFIGDIR=/tmp/spline-vi-mpl python3 scripts/make_spline_vi_thumbnail.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import BSpline

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/img/spline-vi/thumbnail-pastel.png"


def main() -> None:
    x = np.linspace(-0.04, 1.04, 1400)
    step = 0.15
    weights = np.array([0.27, 0.12, 0.12, 0.16, 0.33])
    components = []
    for offset, weight in zip(np.linspace(0.0, 0.4, 5), weights):
        spline = BSpline.basis_element(offset + step * np.arange(5), extrapolate=False)
        # Uniform cubic B-splines have integral equal to their knot spacing.
        density = np.nan_to_num(spline(x), nan=0.0) / step
        components.append(weight * density)
    mixture = np.sum(components, axis=0)

    paper = "#fbfaf8"
    fig = plt.figure(figsize=(4.8, 3.6), dpi=200, facecolor=paper)
    ax = fig.add_axes((0.11, 0.17, 0.78, 0.65))
    ax.set_facecolor(paper)
    ax.set_xlim(-0.04, 1.04)
    ax.set_ylim(-0.10, float(mixture.max()) * 1.28)
    ax.axis("off")

    palette = ["#e6a4af", "#efc18a", "#9ac9b3", "#94bce0", "#b5a0d3"]
    for component, color in zip(components, palette):
        ax.fill_between(x, 0.0, component, color=color, alpha=0.22, linewidth=0)
        visible = component > 1e-5
        ax.plot(x[visible], component[visible], color=color, linewidth=1.7,
                alpha=1.0, solid_capstyle="round", solid_joinstyle="round")
    ax.plot(x, mixture, color="#8e79b2", linewidth=2.8,
            solid_capstyle="round", solid_joinstyle="round")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200, facecolor=paper, pad_inches=0)
    plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
