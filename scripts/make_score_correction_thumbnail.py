"""Minimal project-card artwork: a toy alignment and its score adjustment."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

OUT = Path(__file__).resolve().parents[1] / 'assets/img/score-correction/thumbnail.png'


def main():
    rows=['ACDEFGHIKLMN','ACD-FGHIKL-N','ACDE-GHI-LMN','AC-EFG-IKLMN']
    colors={'residue':'#d7e8e0','gap':'#eed3dc'}
    paper='#fbfaf8'
    fig=plt.figure(figsize=(4.8,3.6),dpi=200,facecolor=paper)
    ax=fig.add_axes((.085,.39,.83,.43))
    ax.set_xlim(0,12);ax.set_ylim(4,0);ax.axis('off')
    for r,row in enumerate(rows):
        for c,a in enumerate(row):
            fill=colors['gap' if a=='-' else 'residue']
            ax.add_patch(FancyBboxPatch((c+.06,r+.06),.88,.88,
                         boxstyle='round,pad=0,rounding_size=.12',facecolor=fill,linewidth=0))
            ax.text(c+.5,r+.51,a,ha='center',va='center',fontfamily='DejaVu Sans Mono',
                    fontsize=9.3,color='#637284')
    ax.add_patch(FancyBboxPatch((3.02,.015),4.96,3.97,
                 boxstyle='round,pad=0,rounding_size=.13',facecolor='none',edgecolor='#b7a2d2',linewidth=1.5))
    bar=fig.add_axes((.085,.16,.83,.15))
    x=np.arange(12)
    # A conceptual score comparison, not a measured search benchmark.
    before=np.array([.45,.65,.82,.92,1.0,.9,.82,.88,.76,.67,.52,.39])
    after=before*np.array([1,1,.92,.67,.63,.7,.63,.74,.88,.92,.85,1])
    bar.bar(x-.16,before,width=.28,color='#c6bddb',linewidth=0)
    bar.bar(x+.16,after,width=.28,color='#94c4b3',linewidth=0)
    bar.set_xlim(-.5,11.5);bar.set_ylim(0,1.12);bar.axis('off')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(OUT,facecolor=paper,pad_inches=0);plt.close(fig)
    print(OUT)


if __name__=='__main__':main()
