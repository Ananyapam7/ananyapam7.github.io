# Editing the VI reading collection

The main introduction remains in _posts/2026-11-21-variational-inference.md.

Each numbered Markdown file here contains one paper's theory. Edit the prose and
LaTeX directly: inline mathematics uses \( ... \) and display mathematics uses
\[ ... \]. You do not need HTML spans or divs in these files.

The papers.json file stores titles, authors, years, source/PDF links, first-page
image paths, the one-sentence contribution, and connections. Its groups array sets
the conceptual reading order. Numbers are stable identifiers from the original
reading list, not a chronology.

After editing, run from the repository:

~~~powershell
python scripts/build_vi_library.py
~~~

This rebuilds _includes/vi-papers.html, which Jekyll includes in the blog.
The script requires the Python Markdown package. Commit the generated include
alongside the notes so the normal Jekyll build needs no Python or extra plugin.

## Adding a paper

1. Add a Markdown note with a new, unused number.
2. Add its metadata to papers.json; use a stable ID such as paper-51.
3. Put a rendered first article page in assets/vi/papers/.
4. Add the ID to a group and connect it to existing papers.
5. Rebuild the include and preview the blog.

Render a first page from a downloaded PDF with Poppler:

~~~powershell
pdftoppm -f 1 -singlefile -scale-to 1000 -png paper.pdf assets/vi/papers/paper-51
~~~

If a PDF has a publisher cover sheet, render the first article page and say so
in the metadata's version field. Link the exact PDF used for the image.

For every note, explain what problem remains, what changes, why the mathematical
step works, and how it connects to the neighboring methods. Keep the general
target pi = gamma / Z, approximation q_phi, and ELBO notation of the introduction.
Use lowercase z for samples; reserve uppercase Z for the normalizing constant.
Keep substantive assumptions for theorem claims, without adding repeated caveats.

## Provenance

The initial collection adapts the 50-paper reading notes supplied by the author.
Titles, authors, dates, and page images were checked against publisher or arXiv
sources. Publication years are shown for published works; preprints are labeled.
Paper 50 intentionally
summarizes arXiv:2602.01412v1 (February 2026); its note links the later revision.

## Method chapters and richer notes

MFVI lives in mfvi.md. CAVI lives in 01.md; its original paper-1 anchor is retained for existing links. Both are marked as methods in papers.json, with the same image/authors/theory layout as research entries. Their featured source papers are Peterson and Anderson (1987) for MFVI and Saul, Jaakkola, and Jordan (1996) for CAVI. The source_title field distinguishes the actual paper title from the method heading. The notes distinguish the general methods from each featured paper's model-specific contribution; neither card claims a uniquely established invention date.

For future expanded notes, develop the problem, intuition, core mathematics, useful settings, and concrete failure modes. Choose a plot or animation that reveals the specific mathematical change. CAVI uses _includes/vi-cavi.html and assets/js/vi-cavi.js; its Gaussian updates are checked with node scripts/test_vi_cavi.cjs. A visual field in metadata inserts the local HTML file at the VISUAL comment in a note.

The research entries 02–50 now include worked intuition and practical limitations,
checked against the linked papers' method and analysis sections. Toy examples in
the explanations are pedagogical calculations, not reproductions of the papers'
experiments. Paper 14 remains a survey entry; MFVI and CAVI remain method chapters.

Concrete (13) and Sticking the Landing (22) include interactive illustrations in
_includes/vi-concrete-demo.html and _includes/vi-stl-demo.html. Their numerical
functions live in assets/js/vi-research-visuals.js; verify them with
node scripts/test_vi_research_visuals.cjs. The Concrete animation starts on request
and respects reduced-motion preferences. The source post loads this script once.


## Notation conventions

- Target: \(\pi=\gamma/Z\). Approximation: \(q_\phi\); factor shorthand \(q_j=q_{\phi_j}\).
- ELBO: \(\mathcal L(\phi)\) for parameters, \(\mathcal L[q]\) for a distribution. A subscript \(j\) means only factor \(j\) varies.
- Iterations: parenthesized superscripts, e.g. \(\phi^{(t)}\), \(q_j^{(t+1)}\). CAVI counts individual factor updates, not sweeps.
- Optimum: star. Estimate: hat. Do not use new/old superscripts. Stored parameters use their last-refresh iteration \(\tau_i\).
- Draws: \(z^{(s)}\), \(s=1,\ldots,K\). Weights: \(w_s=w_\phi(z^{(s)})\), \(\bar w_s=w_s/\sum_r w_r\).
- Base noise: \(\epsilon\sim\nu\). A parameter-dependent transformed noise law is \(\nu_\phi\).
- Gradient estimate: \(\widehat g_\phi\). Variational score: \(S_\phi=\nabla_\phi\log q_\phi\).
- Gaussian mean: \(m\); standard deviation: \(s\); variance: \(v=s^2\); covariance: \(\Sigma\); scale matrix: \(B\).
- Step size: \(\eta_t\). Correlation: \(\rho\). Control-variate parameters: \(\psi\). Local refinement parameters: \(\varphi^{(t)}\).
- Sample size: \(K\). Dataset size: \(N\). Dimension: \(d\). Flow depth: \(L\), with layer index \(\ell\).
- Introduce any specialized symbol locally rather than borrowing a paper's conflicting notation.

## Comparing contributions

Begin each entry with a concrete inference problem that motivates the paper.
Introduce new assumptions and terms before explaining their role, then develop
the core mathematical change and its consequences. Weave the setup and specific
contribution into that narrative rather than opening with a compressed inventory.
Distinguish model structure, variational family, objective, estimator, optimization,
and analysis. State what is retained when that clarifies the comparison. Check
claims against the linked original paper, including its assumptions and version.
Keep years in metadata; omit separate historical-perspective paragraphs.
Do not equate a model-specific source paper with the general method it illustrates.

SVI uses _includes/vi-svi.html and assets/js/vi-svi.js. Its conjugate Gaussian
simulation draws minibatches, fits local factors, and blends natural parameters.
Run node scripts/test_vi_svi.cjs to check minibatch unbiasedness and the profiled
ELBO against an independent Gaussian calculation.

Write for a reader who has not seen the conversation or the source paper. Avoid
headings that answer unintroduced questions. Define specialized terms before
using them in equations, and explain why each new equation is needed.

The interactive network is generated from the same metadata: groups position the
nodes, short supplies their labels, and connections supplies the edges. New entries
appear in the network when you rebuild the include.
