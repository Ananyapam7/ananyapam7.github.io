"""Figures for the spline variational-inference blog post.

Run from an environment that can import the psvi package:

    conda activate general
    python scripts/make_spline_vi_figures.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import torch
from plotly.subplots import make_subplots

SPLINE_VI = Path(__file__).resolve().parents[2] / "spline-vi"
sys.path.insert(0, str(SPLINE_VI))

from psvi import SplineMixture, quadratic_runaway_residual  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "img" / "spline-vi"
OUT.mkdir(parents=True, exist_ok=True)

RESULTS = (
    SPLINE_VI
    / "results"
    / "e2_exact_iwae-20260903T014222Z"
    / "records.jsonl"
)

INK = "#222222"
BLUE = "#1f77b4"
RUST = "#d62728"
GREEN = "#2ca02c"
HAIR = "#b0b0b0"
BASIS_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
PLOTS: dict[str, dict] = {}

plt.rcParams.update(
    {
        "font.size": 11,
        "axes.labelsize": 11,
        "axes.titlesize": 11,
        "legend.fontsize": 9,
        "legend.frameon": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.8,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.grid": False,
    }
)


def dress(axis) -> None:
    axis.tick_params(labelsize=9, colors=INK)
    for label in axis.get_xticklabels() + axis.get_yticklabels():
        label.set_color(INK)


def family(interior_knots: int = 1) -> SplineMixture:
    return SplineMixture(
        interior_knots=interior_knots,
        degree=3,
        dtype=torch.float64,
        root_iterations=40,
        root_tolerance=1e-10,
    )


def grid(n: int = 600) -> torch.Tensor:
    return torch.linspace(0.0, 1.0, n, dtype=torch.float64)


def trapz(y: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
    return torch.trapezoid(y, x, dim=0)


def save(figure: plt.Figure, name: str) -> None:
    figure.savefig(OUT / name, dpi=180, bbox_inches="tight", pad_inches=0.12)
    plt.close(figure)
    print(f"wrote {name}")


def outside_legend(axis, ncol: int) -> None:
    axis.legend(loc="best", frameon=False, fontsize=9)


def _axis(title: str, **extra) -> dict:
    axis = dict(
        title=dict(text=title, font=dict(size=14)),
        showgrid=True,
        gridcolor="rgba(28,28,28,0.07)",
        zeroline=False,
        showline=True,
        linecolor="rgba(28,28,28,0.55)",
        linewidth=1,
        ticks="outside",
        tickcolor="rgba(28,28,28,0.55)",
        ticklen=4,
        tickfont=dict(size=12, color="#222"),
        mirror=False,
    )
    axis.update(extra)
    if axis.get("type") == "log" and axis.get("tickmode") != "array":
        axis["dtick"] = 1
        axis["minor"] = dict(ticks="", showgrid=False)
    return axis


def finish(name: str, fig: go.Figure, height: int = 460, hovermode: str = "x unified") -> None:
    fig.update_layout(
        font=dict(family="Roboto, Helvetica, Arial, sans-serif", size=13, color="#222"),
        height=height,
        autosize=True,
        margin=dict(l=64, r=18, t=58, b=48),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.08,
            x=0,
            xanchor="left",
            font=dict(size=12),
            bgcolor="rgba(255,255,255,0)",
            tracegroupgap=12,
        ),
        hovermode=hovermode,
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="rgba(28,28,28,0.15)",
            font=dict(size=12, color="#222", family="Roboto, Helvetica, Arial, sans-serif"),
            align="left",
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    fig.update_annotations(font=dict(size=13, color="#333"))
    payload = json.loads(fig.to_json())
    payload.get("layout", {}).pop("template", None)
    PLOTS[name] = payload


def figure_mixture() -> dict:
    model = family(1)
    x = grid()
    basis = model.basis(x)
    weights = {
        "example": torch.tensor([0.1, 0.2, 0.4, 0.2, 0.1], dtype=torch.float64),
        "left": torch.tensor([0.46, 0.28, 0.14, 0.08, 0.04], dtype=torch.float64),
        "right": torch.tensor([0.05, 0.10, 0.15, 0.30, 0.40], dtype=torch.float64),
    }
    figure, axes = plt.subplots(1, 2, figsize=(9.2, 3.55))
    for k in range(model.num_basis):
        axes[0].plot(
            x.numpy(),
            basis[:, k].numpy(),
            color=BASIS_COLORS[k],
            lw=1.35,
            label=rf"$b_{k + 1}$",
        )
    axes[0].set(xlabel=r"$e$", ylabel="density", xlim=(0, 1), ylim=(0, None))
    outside_legend(axes[0], ncol=5)
    dress(axes[0])

    styles = {
        "example": (INK, r"example"),
        "left": (BLUE, "weight on the left"),
        "right": (RUST, "weight on the right"),
    }
    for name, gamma in weights.items():
        color, label = styles[name]
        density = model.density(x, gamma)
        axes[1].plot(x.numpy(), density.numpy(), color=color, lw=1.45, label=label)
    axes[1].set(xlabel=r"$e$", xlim=(0, 1), ylim=(0, None))
    outside_legend(axes[1], ncol=3)
    dress(axes[1])
    figure.tight_layout()
    save(figure, "mixture.png")

    interactive = make_subplots(rows=1, cols=2, horizontal_spacing=0.09, subplot_titles=("Basis densities", "Mixtures"))
    interactive.update_layout(template="plotly_white")
    xn = x.numpy()
    for k in range(model.num_basis):
        interactive.add_trace(
            go.Scatter(
                x=xn,
                y=basis[:, k].numpy(),
                mode="lines",
                name=f"b<sub>{k + 1}</sub>",
                line=dict(color=BASIS_COLORS[k], width=2.4),
                hovertemplate="e = %{x:.3f}<br>density = %{y:.3f}<extra></extra>",
            ),
            row=1,
            col=1,
        )
    for name, gamma in weights.items():
        color, label = styles[name]
        interactive.add_trace(
            go.Scatter(
                x=xn,
                y=model.density(x, gamma).numpy(),
                mode="lines",
                name=label,
                line=dict(color=color, width=2.6),
                hovertemplate="e = %{x:.3f}<br>density = %{y:.3f}<extra></extra>",
            ),
            row=1,
            col=2,
        )
    interactive.update_xaxes(_axis("<i>e</i>", range=[0, 1]))
    interactive.update_yaxes(_axis("density", rangemode="tozero"), row=1, col=1)
    interactive.update_yaxes(_axis("density", rangemode="tozero"), row=1, col=2)
    finish("mixture", interactive)
    return {"num_basis": model.num_basis, "degree": model.degree}


def component_moments(model: SplineMixture, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    basis = model.basis(x)
    mean = trapz(x[:, None] * basis, x)
    second = trapz((x[:, None] ** 2) * basis, x)
    variance = (second - mean.square()).clamp_min(0)
    return mean, variance


def relaxation_constant(gamma: torch.Tensor, mean: torch.Tensor, variance: torch.Tensor) -> torch.Tensor:
    """First-order variance contraction constant from the blog.

    ``C = sum_k gamma_k (1-gamma_k) Var(w_k) + (1/2) sum_{k != j} gamma_k gamma_j (m_k-m_j)^2``.
    Diagonal gaps vanish, so the half double-sum is the off-diagonal piece.
    """
    diagonal = (gamma * (1 - gamma) * variance).sum()
    gap = mean[:, None] - mean[None, :]
    cross = 0.5 * (gamma[:, None] * gamma[None, :] * gap.square()).sum()
    return diagonal + cross


def figure_relaxation() -> dict:
    model = family(1)
    gamma = torch.tensor([0.1, 0.2, 0.4, 0.2, 0.1], dtype=torch.float64)
    x = grid(2000)
    mean, variance = component_moments(model, x)
    constant = relaxation_constant(gamma, mean, variance)
    density = model.density(x, gamma)
    mean_mixture = trapz(x * density, x)
    exact_variance = float(trapz((x - mean_mixture) ** 2 * density, x))

    generator = torch.Generator().manual_seed(7)
    draws = 80_000
    component_samples = model.rsample(torch.eye(model.num_basis, dtype=torch.float64), sample_shape=(draws,), generator=generator)
    uniforms = torch.rand(draws, model.num_basis, dtype=torch.float64, generator=generator).clamp(1e-12, 1 - 1e-12)
    gumbel = -torch.log(-torch.log(uniforms))
    temperatures = torch.tensor(
        [0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0, 1.5, 2.0],
        dtype=torch.float64,
    )
    measured = []
    for temperature in temperatures:
        weights = torch.softmax((gamma.log() + gumbel) / temperature, dim=-1)
        blended = (weights * component_samples).sum(-1)
        measured.append(float(blended.var(unbiased=False)))

    figure, axes = plt.subplots(1, 2, figsize=(9.2, 3.55))
    axes[0].plot(x.numpy(), model.density(x, gamma).numpy(), color=INK, lw=1.5, label="exact mixture", zorder=3)
    show = {0.2: BLUE, 1.0: RUST}
    bins = np.linspace(0, 1, 96)
    for temperature, color in show.items():
        weights = torch.softmax((gamma.log() + gumbel) / temperature, dim=-1)
        blended = (weights * component_samples).sum(-1).numpy()
        axes[0].hist(
            blended,
            bins=bins,
            density=True,
            histtype="stepfilled",
            color=color,
            alpha=0.22,
            edgecolor="none",
            linewidth=0,
            label=rf"relaxation, $\Lambda={temperature:g}$",
        )
    axes[0].set(xlabel=r"$e$", ylabel="density", xlim=(0, 1), ylim=(0, None))
    outside_legend(axes[0], ncol=3)
    dress(axes[0])

    temp_np = temperatures.numpy()
    measured_np = np.array(measured)
    linear = exact_variance - temp_np * float(constant)
    local = temp_np <= 0.5
    axes[1].axhline(exact_variance, color=INK, lw=1.0, label="exact mixture")
    axes[1].plot(
        temp_np,
        measured_np,
        color=BLUE,
        marker="o",
        ms=3.6,
        mew=0,
        lw=1.35,
        label="relaxation",
    )
    axes[1].plot(
        temp_np[local],
        linear[local],
        color=RUST,
        ls=(0, (3.2, 1.6)),
        lw=1.25,
        label=r"$\mathrm{Var}(e_0)-\Lambda C$",
    )
    axes[1].set(xlabel=r"temperature $\Lambda$", ylabel=r"$\mathrm{Var}(e)$", xlim=(0, 2.05), ylim=(0, None))
    outside_legend(axes[1], ncol=1)
    dress(axes[1])
    figure.tight_layout()
    save(figure, "relaxation.png")

    interactive = make_subplots(
        rows=1,
        cols=2,
        horizontal_spacing=0.09,
        subplot_titles=("Density", "Variance"),
    )
    interactive.update_layout(template="plotly_white", barmode="overlay", bargap=0)
    shown = {}
    for temperature, color in show.items():
        weights = torch.softmax((gamma.log() + gumbel) / temperature, dim=-1)
        blended = (weights * component_samples).sum(-1).numpy()
        counts, edges = np.histogram(blended, bins=bins, density=True)
        shown[temperature] = (counts, edges, color)
    for temperature, (counts, edges, color) in shown.items():
        interactive.add_trace(
            go.Bar(
                x=(edges[:-1] + edges[1:]) / 2,
                y=counts,
                width=float(edges[1] - edges[0]),
                name=f"relaxation, Λ = {temperature:g}",
                marker=dict(color=color, opacity=0.38, line=dict(width=0)),
                hovertemplate="e = %{x:.3f}<br>density = %{y:.3f}<extra></extra>",
            ),
            row=1,
            col=1,
        )
    interactive.add_trace(
        go.Scatter(
            x=x.numpy(),
            y=density.numpy(),
            mode="lines",
            name="exact mixture",
            line=dict(color=INK, width=2.6),
            hovertemplate="e = %{x:.3f}<br>density = %{y:.3f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    interactive.add_trace(
        go.Scatter(
            x=[0, 2.05],
            y=[exact_variance, exact_variance],
            mode="lines",
            name="exact variance",
            line=dict(color=INK, width=2),
            hovertemplate="Var = %{y:.4f}<extra></extra>",
        ),
        row=1,
        col=2,
    )
    interactive.add_trace(
        go.Scatter(
            x=temp_np,
            y=measured_np,
            mode="lines+markers",
            name="relaxation",
            line=dict(color=BLUE, width=2.4),
            marker=dict(size=7, color=BLUE),
            hovertemplate="Λ = %{x:.2f}<br>Var = %{y:.4f}<extra></extra>",
        ),
        row=1,
        col=2,
    )
    interactive.add_trace(
        go.Scatter(
            x=temp_np[local],
            y=linear[local],
            mode="lines",
            name="Var(e₀) − ΛC",
            line=dict(color=RUST, width=2.2, dash="dash"),
            hovertemplate="Λ = %{x:.2f}<br>Var ≈ %{y:.4f}<extra></extra>",
        ),
        row=1,
        col=2,
    )
    interactive.update_xaxes(_axis("<i>e</i>", range=[0, 1]), row=1, col=1)
    interactive.update_yaxes(_axis("density", rangemode="tozero"), row=1, col=1)
    interactive.update_xaxes(_axis("temperature Λ", range=[0, 2.05]), row=1, col=2)
    interactive.update_yaxes(_axis("Var(<i>e</i>)", rangemode="tozero"), row=1, col=2)
    finish("relaxation", interactive, hovermode="closest")
    return {
        "exact_variance": exact_variance,
        "C": float(constant),
        "temperatures": temp_np.tolist(),
        "measured_variance": measured_np.tolist(),
        "linear": linear.tolist(),
        "component_means": mean.tolist(),
        "component_variances": variance.tolist(),
    }


def figure_cdf() -> dict:
    model = family(1)
    gamma = torch.tensor([0.1, 0.2, 0.4, 0.2, 0.1], dtype=torch.float64)
    x = grid(800)
    density = model.density(x, gamma)
    closed = model.cdf(x, gamma)
    # Cumulative integral of the plotted density, for the identity check.
    dx = x[1] - x[0]
    cumulative = torch.cumsum(density, 0) * dx
    cumulative = cumulative - cumulative[0]
    gap = (closed - cumulative).abs()

    figure, axes = plt.subplots(1, 2, figsize=(9.2, 3.55))
    axes[0].fill_between(x.numpy(), density.numpy(), color=BLUE, alpha=0.12, lw=0)
    axes[0].plot(x.numpy(), density.numpy(), color=BLUE, lw=1.45)
    axes[0].set(xlabel=r"$e$", ylabel=r"$q_\gamma(e)$", xlim=(0, 1), ylim=(0, None))
    dress(axes[0])

    axes[1].plot(x.numpy(), x.numpy(), color=HAIR, lw=1.0, ls=(0, (2.4, 1.8)), label="uniform CDF")
    axes[1].plot(x.numpy(), closed.numpy(), color=INK, lw=1.5, label="degree-raised spline")
    mark = slice(None, None, 70)
    axes[1].plot(
        x[mark].numpy(),
        cumulative[mark].numpy(),
        ls="none",
        marker="o",
        ms=3.2,
        mfc="white",
        mew=0.9,
        color=RUST,
        label="integral of the density",
    )
    axes[1].set(xlabel=r"$e$", ylabel=r"$F_\gamma(e)$", xlim=(0, 1), ylim=(-0.02, 1.02))
    outside_legend(axes[1], ncol=1)
    dress(axes[1])
    figure.tight_layout()
    save(figure, "cdf.png")

    interactive = make_subplots(rows=1, cols=2, horizontal_spacing=0.09, subplot_titles=("Density", "CDF"))
    interactive.update_layout(template="plotly_white")
    xn = x.numpy()
    interactive.add_trace(
        go.Scatter(
            x=np.concatenate([xn, xn[::-1]]),
            y=np.concatenate([density.numpy(), np.zeros_like(xn)]),
            fill="toself",
            mode="lines",
            line=dict(color="rgba(31,119,180,0)"),
            fillcolor="rgba(31,119,180,0.16)",
            hoverinfo="skip",
            showlegend=False,
        ),
        row=1,
        col=1,
    )
    interactive.add_trace(
        go.Scatter(
            x=xn,
            y=density.numpy(),
            mode="lines",
            name="mixture density",
            line=dict(color=BLUE, width=2.6),
            hovertemplate="e = %{x:.3f}<br>q = %{y:.3f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    interactive.add_trace(
        go.Scatter(
            x=xn,
            y=xn,
            mode="lines",
            name="uniform CDF",
            line=dict(color="#9aa0a6", width=1.6, dash="dot"),
            hovertemplate="e = %{x:.3f}<br>F = %{y:.3f}<extra></extra>",
        ),
        row=1,
        col=2,
    )
    interactive.add_trace(
        go.Scatter(
            x=xn,
            y=closed.numpy(),
            mode="lines",
            name="degree-raised spline",
            line=dict(color=INK, width=2.6),
            hovertemplate="e = %{x:.3f}<br>F = %{y:.3f}<extra></extra>",
        ),
        row=1,
        col=2,
    )
    interactive.add_trace(
        go.Scatter(
            x=x[mark].numpy(),
            y=cumulative[mark].numpy(),
            mode="markers",
            name="integral of the density",
            marker=dict(size=8, color="white", line=dict(color=RUST, width=1.6)),
            hovertemplate="e = %{x:.3f}<br>integral = %{y:.3f}<extra></extra>",
        ),
        row=1,
        col=2,
    )
    interactive.update_xaxes(_axis("<i>e</i>", range=[0, 1]))
    interactive.update_yaxes(_axis("q<sub>γ</sub>(e)", rangemode="tozero"), row=1, col=1)
    interactive.update_yaxes(_axis("F<sub>γ</sub>(e)", range=[-0.02, 1.02]), row=1, col=2)
    finish("cdf", interactive)
    return {"max_abs_gap_to_trapezoid": float(gap.max()), "cdf_ends": [float(closed[0]), float(closed[-1])]}


def figure_sampler() -> dict:
    model = family(1)
    gamma = torch.tensor([0.1, 0.2, 0.4, 0.2, 0.1], dtype=torch.float64)
    x = grid(800)
    density = model.density(x, gamma)
    generator = torch.Generator().manual_seed(11)
    draws = 40_000
    samples = model.rsample(gamma, sample_shape=(draws,), generator=generator)
    transformed = model.cdf(samples, gamma)

    # Ambient pathwise derivatives on the interior, where the density is not tiny.
    interior = x[(density > 0.15)]
    denominator = model.density(interior, gamma)
    partials = []
    for k in range(model.num_basis):
        one = torch.zeros(model.num_basis, dtype=torch.float64)
        one[k] = 1.0
        numerator = model.cdf(interior, one)
        partials.append((-numerator / denominator).numpy())

    figure, axes = plt.subplots(1, 2, figsize=(9.2, 3.55))
    axes[0].hist(
        samples.numpy(),
        bins=np.linspace(0, 1, 120),
        density=True,
        color=BLUE,
        alpha=0.22,
        edgecolor="none",
        linewidth=0,
        label="inverse-CDF samples",
    )
    axes[0].plot(x.numpy(), density.numpy(), color=INK, lw=1.45, label="mixture density")
    axes[0].set(xlabel=r"$e$", ylabel="density", xlim=(0, 1), ylim=(0, None))
    outside_legend(axes[0], ncol=2)
    dress(axes[0])

    for k, values in enumerate(partials):
        axes[1].plot(interior.numpy(), values, color=BASIS_COLORS[k], lw=1.3, label=rf"$k={k + 1}$")
    axes[1].axhline(0, color=HAIR, lw=0.7)
    axes[1].set(xlabel=r"$e$", ylabel=r"$\partial e/\partial\gamma_k$")
    outside_legend(axes[1], ncol=5)
    dress(axes[1])
    figure.tight_layout()
    save(figure, "sampler.png")

    interactive = make_subplots(rows=1, cols=2, horizontal_spacing=0.1, subplot_titles=("Samples", "Implicit derivatives"))
    interactive.update_layout(template="plotly_white", barmode="overlay", bargap=0)
    sample_np = samples.numpy()
    edges = np.linspace(0, 1, 48)
    counts, edges = np.histogram(sample_np, bins=edges, density=True)
    interactive.add_trace(
        go.Bar(
            x=(edges[:-1] + edges[1:]) / 2,
            y=counts,
            width=float(edges[1] - edges[0]),
            name="inverse-CDF samples",
            marker=dict(color="rgba(31,119,180,0.35)", line=dict(width=0)),
            hovertemplate="e = %{x:.3f}<br>density = %{y:.3f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    interactive.add_trace(
        go.Scatter(
            x=x.numpy(),
            y=density.numpy(),
            mode="lines",
            name="mixture density",
            line=dict(color=INK, width=2.6),
            hovertemplate="e = %{x:.3f}<br>density = %{y:.3f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    for k, values in enumerate(partials):
        interactive.add_trace(
            go.Scatter(
                x=interior.numpy(),
                y=values,
                mode="lines",
                name=f"k = {k + 1}",
                line=dict(color=BASIS_COLORS[k], width=2.3),
                hovertemplate="e = %{x:.3f}<br>∂e/∂γ = %{y:.3f}<extra></extra>",
            ),
            row=1,
            col=2,
        )
    interactive.update_xaxes(_axis("<i>e</i>", range=[0, 1]), row=1, col=1)
    interactive.update_yaxes(_axis("density", rangemode="tozero"), row=1, col=1)
    interactive.update_xaxes(_axis("<i>e</i>"), row=1, col=2)
    interactive.update_yaxes(_axis("∂e / ∂γ<sub>k</sub>"), row=1, col=2)
    finish("sampler", interactive, hovermode="closest")

    # Kolmogorov-Smirnov statistic against Uniform(0, 1), without a p-value claim.
    ordered = torch.sort(transformed.clamp(0, 1)).values
    n = ordered.numel()
    index = torch.arange(1, n + 1, dtype=torch.float64)
    d_plus = (index / n - ordered).max()
    d_minus = (ordered - (index - 1) / n).max()
    return {
        "draws": draws,
        "pit_ks": float(torch.maximum(d_plus, d_minus)),
        "sample_mean": float(samples.mean()),
        "sample_var": float(samples.var(unbiased=False)),
    }


def figure_stratified() -> None:
    model = family(1)
    gamma = torch.tensor([0.1, 0.2, 0.4, 0.2, 0.1], dtype=torch.float64)
    x = grid()
    density = model.density(x, gamma)
    count = 32
    generator = torch.Generator().manual_seed(4)
    iid = torch.rand(count, dtype=torch.float64, generator=generator)
    within = torch.rand(count, dtype=torch.float64, generator=generator)
    stratified = (torch.arange(count, dtype=torch.float64) + within) / count
    iid_e = model.icdf(iid, gamma)
    stratified_e = model.icdf(stratified, gamma)

    figure, axes = plt.subplots(1, 2, figsize=(9.2, 3.35), sharex=True, sharey=True)
    ceiling = float(density.max()) * 1.12
    for axis, points, label, color in (
        (axes[0], iid_e, "independent uniforms", RUST),
        (axes[1], stratified_e, "one draw in each stratum", BLUE),
    ):
        axis.fill_between(x.numpy(), density.numpy(), color=BLUE, alpha=0.08, lw=0)
        axis.plot(x.numpy(), density.numpy(), color=INK, lw=1.6)
        axis.vlines(points.numpy(), 0, ceiling * 0.06, color=color, lw=1.1)
        axis.set(xlabel=r"$e$", xlim=(0, 1), ylim=(0, ceiling), title=label)
        axis.title.set_fontsize(10)
        axis.title.set_color(INK)
        dress(axis)
    axes[0].set_ylabel("density")
    figure.tight_layout()
    save(figure, "stratified.png")

    interactive = make_subplots(
        rows=1,
        cols=2,
        shared_yaxes=True,
        horizontal_spacing=0.06,
        subplot_titles=("Independent uniforms", "One draw in each stratum"),
    )
    interactive.update_layout(template="plotly_white")
    xn = x.numpy()
    yn = density.numpy()
    for column, points, label, color in (
        (1, iid_e.numpy(), "independent draws", RUST),
        (2, stratified_e.numpy(), "stratified draws", BLUE),
    ):
        interactive.add_trace(
            go.Scatter(
                x=np.concatenate([xn, xn[::-1]]),
                y=np.concatenate([yn, np.zeros_like(xn)]),
                fill="toself",
                mode="lines",
                line=dict(width=0, color="rgba(0,0,0,0)"),
                fillcolor="rgba(31,119,180,0.08)",
                hoverinfo="skip",
                showlegend=False,
            ),
            row=1,
            col=column,
        )
        interactive.add_trace(
            go.Scatter(
                x=xn,
                y=yn,
                mode="lines",
                name="mixture density",
                line=dict(color=INK, width=2.5),
                showlegend=column == 1,
                hovertemplate="e = %{x:.3f}<br>density = %{y:.3f}<extra></extra>",
            ),
            row=1,
            col=column,
        )
        interactive.add_trace(
            go.Scatter(
                x=points,
                y=np.full(points.shape, ceiling * 0.035),
                mode="markers",
                name=label,
                marker=dict(symbol="line-ns", size=14, color=color, line=dict(width=2, color=color)),
                hovertemplate="sample e = %{x:.3f}<extra></extra>",
            ),
            row=1,
            col=column,
        )
    interactive.update_xaxes(_axis("<i>e</i>", range=[0, 1]))
    interactive.update_yaxes(_axis("density", range=[0, ceiling]), row=1, col=1)
    finish("stratified", interactive, height=420, hovermode="closest")


def figure_runaway() -> dict:
    eigenvalues = torch.tensor([0.25, 0.6, 1.2, 2.5, 5.0], dtype=torch.float64)
    coefficients = torch.tensor([0.55, 0.45, 0.40, 0.35, 0.30], dtype=torch.float64)
    coefficients = coefficients / coefficients.norm()
    smoothing = torch.logspace(-2, 2, 240, dtype=torch.float64)
    residual = quadratic_runaway_residual(eigenvalues, coefficients, smoothing)
    beta = coefficients / (1 + smoothing[:, None] * eigenvalues)

    figure, axes = plt.subplots(1, 2, figsize=(9.2, 3.55))
    for k in range(eigenvalues.numel()):
        axes[0].plot(
            smoothing.numpy(),
            beta[:, k].numpy(),
            color=BASIS_COLORS[k],
            lw=1.3,
            label=rf"$d={eigenvalues[k].item():g}$",
        )
    axes[0].set_xscale("log")
    axes[0].set(xlabel=r"penalty $\lambda$", ylabel=r"whitened coefficient $\beta_k(\lambda)$")
    outside_legend(axes[0], ncol=5)
    dress(axes[0])

    axes[1].plot(smoothing.numpy(), residual.numpy(), color=INK, lw=1.45)
    axes[1].axhline(0, color=HAIR, lw=0.7)
    axes[1].set_xscale("log")
    axes[1].set_ylim(bottom=0)
    axes[1].set(
        xlabel=r"penalty $\lambda$",
        ylabel=r"$\{\mathrm{edf}-\nu\}-\lambda R$",
    )
    dress(axes[1])
    figure.tight_layout()
    save(figure, "runaway.png")

    interactive = make_subplots(rows=1, cols=2, horizontal_spacing=0.1, subplot_titles=("Whitened coefficients", "Smoothing residual"))
    interactive.update_layout(template="plotly_white")
    lam = smoothing.numpy()
    for k in range(eigenvalues.numel()):
        interactive.add_trace(
            go.Scatter(
                x=lam,
                y=beta[:, k].numpy(),
                mode="lines",
                name=f"d = {eigenvalues[k].item():g}",
                line=dict(color=BASIS_COLORS[k], width=2.3),
                hovertemplate="λ = %{x:.3g}<br>β = %{y:.3f}<extra></extra>",
            ),
            row=1,
            col=1,
        )
    interactive.add_trace(
        go.Scatter(
            x=lam,
            y=residual.numpy(),
            mode="lines",
            name="residual",
            line=dict(color=INK, width=2.6),
            hovertemplate="λ = %{x:.3g}<br>residual = %{y:.3f}<extra></extra>",
        ),
        row=1,
        col=2,
    )
    interactive.update_xaxes(_axis("penalty λ", type="log"), row=1, col=1)
    interactive.update_xaxes(_axis("penalty λ", type="log"), row=1, col=2)
    interactive.update_yaxes(_axis("whitened coefficient β<sub>k</sub>(λ)"), row=1, col=1)
    interactive.update_yaxes(_axis("{edf − ν} − λR", rangemode="tozero"), row=1, col=2)
    finish("runaway", interactive)
    return {
        "min_residual": float(residual.min()),
        "max_residual": float(residual.max()),
        "coefficient_norm": float(coefficients.norm()),
    }


def _records() -> list[dict]:
    rows = []
    for line in RESULTS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def figure_penalty() -> dict:
    rows = _records()
    curves = [row for row in rows if row["method"] == "oracle_rise_curve"]
    fellner = [row for row in rows if row["method"] == "fellner_schall_exact_iwae"]
    sizes = [100, 200, 400]
    colors = {100: BLUE, 200: GREEN, 400: RUST}

    figure, axes = plt.subplots(1, 2, figsize=(9.2, 3.55))
    summary = {}
    for size in sizes:
        selected = [row for row in curves if row["observations"] == size]
        grid_lambda = np.array(selected[0]["smoothing_grid"], dtype=float)
        stack = np.array([row["evaluation_rise_curve"] for row in selected], dtype=float)
        curve = stack.mean(axis=0)
        axes[0].plot(grid_lambda, curve, color=colors[size], lw=1.35, label=rf"$n={size}$")
        oracle = float(np.median([row["oracle_smoothing"] for row in selected]))
        nearest = int(np.argmin(np.abs(grid_lambda - oracle)))
        axes[0].scatter(
            [grid_lambda[nearest]],
            [curve[nearest]],
            color=colors[size],
            s=16,
            zorder=3,
            linewidths=0,
        )
        oracles = np.array([row["oracle_smoothing"] for row in selected], dtype=float)
        fs = np.array(
            [row["smoothing"] for row in fellner if row["observations"] == size],
            dtype=float,
        )
        summary[str(size)] = {
            "marked_oracle_grid": float(grid_lambda[nearest]),
            "median_oracle": float(np.median(oracles)),
            "median_fellner": float(np.median(fs)),
            "oracle_over_n": float(np.median(oracles) / size),
        }
    axes[0].set_xscale("log")
    axes[0].set(xlabel=r"penalty $\lambda$", ylabel="evaluation RISE")
    outside_legend(axes[0], ncol=3)
    dress(axes[0])

    oracle_med = [summary[str(size)]["median_oracle"] for size in sizes]
    fellner_med = [summary[str(size)]["median_fellner"] for size in sizes]
    axes[1].plot(sizes, oracle_med, color=INK, marker="o", ms=4.2, mew=0, lw=1.35, label=r"RISE-optimal $\lambda^*$")
    axes[1].plot(sizes, fellner_med, color=BLUE, marker="o", ms=4.2, mew=0, lw=1.35, label="Fellner–Schall")
    reference_n = np.array([80, 480], dtype=float)
    axes[1].plot(reference_n, 0.17 * reference_n, color=RUST, ls=(0, (3.2, 1.6)), lw=1.15, label=r"$0.17\,n$")
    for size in sizes:
        oracle_seeds = [
            row["oracle_smoothing"] for row in curves if row["observations"] == size
        ]
        fs_seeds = [row["smoothing"] for row in fellner if row["observations"] == size]
        axes[1].scatter(np.full(len(oracle_seeds), size), oracle_seeds, color=INK, s=11, alpha=0.28, linewidths=0, zorder=2)
        axes[1].scatter(np.full(len(fs_seeds), size), fs_seeds, color=BLUE, s=11, alpha=0.28, linewidths=0, zorder=2)
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set(xlabel=r"sample size $n$", ylabel=r"penalty $\lambda$")
    outside_legend(axes[1], ncol=3)
    dress(axes[1])
    figure.tight_layout()
    save(figure, "penalty.png")

    interactive = make_subplots(rows=1, cols=2, horizontal_spacing=0.1, subplot_titles=("Evaluation RISE", "Selected penalties"))
    interactive.update_layout(template="plotly_white")
    for size in sizes:
        selected = [row for row in curves if row["observations"] == size]
        grid_lambda = np.array(selected[0]["smoothing_grid"], dtype=float)
        stack = np.array([row["evaluation_rise_curve"] for row in selected], dtype=float)
        curve = stack.mean(axis=0)
        nearest = int(np.argmin(np.abs(grid_lambda - summary[str(size)]["median_oracle"])))
        interactive.add_trace(
            go.Scatter(
                x=grid_lambda,
                y=curve,
                mode="lines",
                name=f"n = {size}",
                line=dict(color=colors[size], width=2.3),
                hovertemplate="λ = %{x:.3g}<br>RISE = %{y:.4f}<extra></extra>",
            ),
            row=1,
            col=1,
        )
        interactive.add_trace(
            go.Scatter(
                x=[grid_lambda[nearest]],
                y=[curve[nearest]],
                mode="markers",
                name=f"oracle, n = {size}",
                marker=dict(size=9, color=colors[size], line=dict(color="white", width=1)),
                showlegend=False,
                hovertemplate="oracle λ = %{x:.2f}<br>RISE = %{y:.4f}<extra></extra>",
            ),
            row=1,
            col=1,
        )
    interactive.add_trace(
        go.Scatter(
            x=sizes,
            y=oracle_med,
            mode="lines+markers",
            name="RISE-optimal λ*",
            line=dict(color=INK, width=2.4),
            marker=dict(size=8, color=INK),
            hovertemplate="n = %{x:.0f}<br>λ* = %{y:.2f}<extra></extra>",
        ),
        row=1,
        col=2,
    )
    interactive.add_trace(
        go.Scatter(
            x=sizes,
            y=fellner_med,
            mode="lines+markers",
            name="Fellner–Schall",
            line=dict(color=BLUE, width=2.4),
            marker=dict(size=8, color=BLUE),
            hovertemplate="n = %{x:.0f}<br>λ = %{y:.2f}<extra></extra>",
        ),
        row=1,
        col=2,
    )
    interactive.add_trace(
        go.Scatter(
            x=reference_n,
            y=0.17 * reference_n,
            mode="lines",
            name="0.17 n",
            line=dict(color=RUST, width=2, dash="dash"),
            hovertemplate="n = %{x:.0f}<br>0.17n = %{y:.2f}<extra></extra>",
        ),
        row=1,
        col=2,
    )
    for size in sizes:
        oracle_seeds = [row["oracle_smoothing"] for row in curves if row["observations"] == size]
        fs_seeds = [row["smoothing"] for row in fellner if row["observations"] == size]
        interactive.add_trace(
            go.Scatter(
                x=np.full(len(oracle_seeds), size),
                y=oracle_seeds,
                mode="markers",
                showlegend=False,
                marker=dict(size=7, color=INK, opacity=0.35),
                hovertemplate="seed oracle λ = %{y:.2f}<extra></extra>",
            ),
            row=1,
            col=2,
        )
        interactive.add_trace(
            go.Scatter(
                x=np.full(len(fs_seeds), size),
                y=fs_seeds,
                mode="markers",
                showlegend=False,
                marker=dict(size=7, color=BLUE, opacity=0.35),
                hovertemplate="seed Fellner–Schall λ = %{y:.2f}<extra></extra>",
            ),
            row=1,
            col=2,
        )
    interactive.update_xaxes(_axis("penalty λ", type="log", tickmode="array", tickvals=[1, 10, 100]), row=1, col=1)
    interactive.update_yaxes(_axis("evaluation RISE"), row=1, col=1)
    interactive.update_xaxes(_axis("sample size <i>n</i>", type="log", tickmode="array", tickvals=[100, 200, 400]), row=1, col=2)
    interactive.update_yaxes(_axis("penalty λ", type="log", tickmode="array", tickvals=[10, 20, 40, 80]), row=1, col=2)
    finish("penalty", interactive, hovermode="closest")
    return summary


def figure_thumbnail() -> None:
    """Square card of the three example mixtures.

    The blog list shows this at the column width with a 1:1 aspect ratio,
    so the file is exactly 1200 by 1200.
    """
    model = family(1)
    x = grid()
    xn = x.numpy()
    weights = (
        ("#1f77b4", torch.tensor([0.46, 0.28, 0.14, 0.08, 0.04], dtype=torch.float64)),
        ("#222222", torch.tensor([0.1, 0.2, 0.4, 0.2, 0.1], dtype=torch.float64)),
        ("#d62728", torch.tensor([0.05, 0.10, 0.15, 0.30, 0.40], dtype=torch.float64)),
    )
    paper = "#f7f6f4"
    figure = plt.figure(figsize=(6.0, 6.0), dpi=200, facecolor=paper)
    axis = figure.add_axes((0.0, 0.0, 1.0, 1.0))
    axis.set_facecolor(paper)
    drawn = []
    for color, gamma in weights:
        density = model.density(x, gamma).numpy()
        drawn.append(density)
        axis.fill_between(xn, density, 0.0, color=color, alpha=0.13, linewidth=0)
        axis.plot(xn, density, color=color, lw=3.6, solid_capstyle="butt", solid_joinstyle="round")
    peak = float(max(curve.max() for curve in drawn))
    axis.set_xlim(0.0, 1.0)
    axis.set_ylim(0.0, peak * 1.04)
    axis.set_xticks([])
    axis.set_yticks([])
    for spine in axis.spines.values():
        spine.set_visible(False)
    figure.savefig(OUT / "thumbnail.png", dpi=200, facecolor=paper, pad_inches=0)
    plt.close(figure)
    print("wrote thumbnail.png")


def main() -> None:
    report = {
        "mixture": figure_mixture(),
        "relaxation": figure_relaxation(),
        "cdf": figure_cdf(),
        "sampler": figure_sampler(),
        "runaway": figure_runaway(),
        "penalty": figure_penalty(),
    }
    figure_stratified()
    payload = json.dumps(PLOTS, separators=(",", ":"))
    plot_path = ROOT / "assets" / "js" / "spline-vi-plots.json"
    plot_path.write_text(payload, encoding="utf-8")
    data_path = ROOT / "assets" / "js" / "spline-vi-plots-data.js"
    data_path.write_text("window.SPLINE_VI_PLOTS=" + payload + ";\n", encoding="utf-8")
    print(f"wrote {data_path.name} ({data_path.stat().st_size} bytes)")
    notes = Path(__file__).with_name("spline_vi_figure_notes.json")
    notes.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "thumbnail":
        figure_thumbnail()
    else:
        main()
