"""Illustrative, reproducible figures for the Score Correction project page.

These are toy alignments and arithmetic examples, not benchmark results.
Run with MPLCONFIGDIR=/tmp/score-correction-mpl python3 scripts/make_score_correction_figures.py.
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle
import numpy as np

OUT = Path(__file__).resolve().parents[1] / 'assets/img/score-correction'
INK, BLUE, TEAL, ROSE = '#33465b', '#7395b4', '#66a79a', '#cf98a7'
RESIDUE, GAP = '#dbece6', '#f2f0ef'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'text.color': INK, 'axes.labelcolor': INK,
                     'xtick.color': INK, 'ytick.color': INK,
                     'axes.spines.top': False, 'axes.spines.right': False})


def toy_alignments():
    sequence = 'ACDEFGHIKLMNPQRSTV'
    terminal = [sequence] + ['-' * 9 + sequence[9:]] * 5
    fragmented = [sequence] + [''.join(a if j % 2 == 0 else '-' for j, a in enumerate(sequence))] * 5
    return terminal, fragmented


def corrections(rows, radius=2, beta=1 / 3):
    residues = np.array([[a != '-' for a in row] for row in rows])
    n = residues.shape[1]
    centers = np.arange(radius, n - radius)
    fraction, raw = [], []
    for center in centers:
        block = residues[:, center-radius:center+radius+1]
        active = block.any(axis=1)
        f = float(block.all(axis=1).sum() / active.sum())
        fraction.append(f)
        raw.append(np.log2((beta + f) / (beta + 1)))
    raw = np.array(raw)
    corrected = np.array([raw[np.abs(centers-i) <= radius].max() for i in range(n)])
    return centers, np.array(fraction), raw, corrected


def alignment_windows():
    terminal, fragmented = toy_alignments()
    assert sum(row.count('-') for row in terminal) == sum(row.count('-') for row in fragmented)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), dpi=180)
    for ax, rows, title, subtitle in zip(
        axes, [terminal, fragmented],
        ['Missing prefix, continuous fragment', 'Repeated interruptions'],
        ['Highlighted window: 1 of 1 observed rows is gap-free',
         'Highlighted window: 1 of 6 observed rows is gap-free']):
        matrix = np.array([[a != '-' for a in row] for row in rows], dtype=int)
        ax.imshow(matrix, cmap=ListedColormap([GAP, RESIDUE]), vmin=0, vmax=1, aspect='auto')
        for r, row in enumerate(rows):
            for c, a in enumerate(row):
                ax.text(c, r, a, ha='center', va='center', fontsize=9, family='DejaVu Sans Mono',
                        color=INK if a != '-' else '#a09b9a')
        ax.add_patch(Rectangle((1.5, -0.5), 5, 6, fill=False, ec=BLUE, lw=2))
        ax.set_title(title, fontsize=12, fontweight='bold', loc='left', pad=15)
        ax.set_xticks([0, 5, 8, 12, 17], ['1', '6', '9', '13', '18'])
        ax.set_yticks(range(6), [f'Seq {i+1}' for i in range(6)])
        ax.tick_params(length=0, pad=7)
        ax.set_xlabel('Alignment column', labelpad=9)
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.text(0, -0.27, subtitle, transform=ax.transAxes, fontsize=9, va='top')
    fig.subplots_adjust(left=.055, right=.99, bottom=.28, top=.83, wspace=.23)
    fig.savefig(OUT / 'alignment-windows.png', facecolor='white')
    plt.close(fig)


def boundary_correction():
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 3.6), dpi=180)
    for ax, rows, title in zip(axes, toy_alignments(), ['One fragment boundary', 'Frequent internal gaps']):
        centers, fractions, raw, corrected = corrections(rows)
        if title == 'One fragment boundary':
            assert np.allclose(corrected, 0)
            assert np.isclose(fractions[0], 1)
        else:
            assert np.allclose(fractions, 1/6)
            assert np.all(corrected < 0)
        ax.plot(centers+1, raw, '--o', color=ROSE, lw=1.7, markersize=3, label='Local window adjustment')
        ax.plot(np.arange(1, len(rows[0])+1), corrected, color=TEAL, lw=2.8,
                label='After choosing the least severe window')
        ax.set_title(title, loc='left', fontsize=12, fontweight='bold', pad=15)
        ax.set_xlabel('Alignment column')
        ax.set_ylim(-2.1, .22)
        ax.set_yticks([-2, -1, 0])
        ax.set_xticks([1, 5, 9, 13, 18])
        ax.spines['left'].set_color('#d5dade')
        ax.spines['bottom'].set_color('#d5dade')
        ax.grid(axis='y', color='#edf0f2', linewidth=.8)
    axes[0].set_ylabel('Score adjustment (bits)')
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=2, frameon=False, fontsize=9)
    fig.subplots_adjust(left=.065, right=.99, bottom=.28, top=.82, wspace=.2)
    fig.savefig(OUT / 'boundary-correction.png', facecolor='white')
    plt.close(fig)


def decoy_example():
    before = np.array([4., 7., 10., 9., 6., 4.])
    threshold = 24.
    alpha = (before.sum()-threshold) / before.sum()
    after = before * (1-alpha)
    assert before.sum() == 40 and np.isclose(alpha, .4) and np.isclose(after.sum(), threshold)
    fig, ax = plt.subplots(figsize=(9.5, 3.8), dpi=180)
    x = np.arange(6)
    ax.bar(x-.18, before, width=.34, color=BLUE, label='Before: total score 40')
    ax.bar(x+.18, after, width=.34, color=TEAL, label='After: total score 24')
    for i, (a,b) in enumerate(zip(before,after)):
        ax.text(i-.18,a+.2,f'{a:g}',ha='center',fontsize=9)
        ax.text(i+.18,b+.2,f'{b:g}',ha='center',fontsize=9)
    ax.set_xticks(x,[f'Column {i+1}' for i in x])
    ax.set_ylim(0,12)
    ax.set_ylabel('Match-score contribution (bits)')
    ax.set_title('Illustrative decoy: remove 40% of each contribution to reach the cutoff',
                 fontsize=11, fontweight='bold', loc='left',pad=18)
    ax.set_axisbelow(True)
    ax.grid(axis='y',color='#edf0f2',linewidth=.8)
    ax.spines['left'].set_color('#d5dade')
    ax.spines['bottom'].set_color('#d5dade')
    ax.legend(frameon=False,loc='upper right',fontsize=9)
    fig.subplots_adjust(left=.08,right=.99,bottom=.15,top=.82)
    fig.savefig(OUT / 'decoy-example.png',facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    alignment_windows()
    boundary_correction()
    decoy_example()
    print('Generated three illustrative figures; arithmetic and boundary-case checks passed.')
