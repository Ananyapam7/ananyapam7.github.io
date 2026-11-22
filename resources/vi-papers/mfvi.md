Learning a Boltzmann machine requires correlations between its binary units. Estimating those correlations by repeated stochastic simulation is expensive. Peterson and Anderson replace this sampling step with deterministic mean-field equations.

**Replace fluctuating neighbors by their averages.** In our notation, let the binary units be \(z_j\in\{-1,1\}\), with means \(m_j=\mathbb E_q[z_j]\). For symmetric couplings \(W_{jk}\), biases \(b_j\), and temperature \(T>0\), the mean-field equations take the form

\[
m_j=\tanh\!\left(\frac{b_j+\sum_{k\ne j}W_{jk}m_k}{T}\right),
\qquad \mathbb E_q[z_jz_k]=m_jm_k\quad(j\ne k).
\]

Each unit responds to the average field produced by the others. The resulting products of means approximate the correlations used in the learning rule, in both the clamped and free phases. This is the paper's computational change: deterministic approximate correlations replace expensive stochastic measurements.

The transferable variational idea is to fit independent factors:

\[
q_\phi(z)=\prod_{j=1}^Jq_{\phi_j}(z_j).
\]

We abbreviate each factor as \(q_j\). Under \(q_1(z_1)q_2(z_2)\), drawing a large \(z_1\) does not make a large \(z_2\) more likely. Each block can still contain several dependent unknowns; independence is imposed between blocks.

This makes sampling and density evaluation simple: draw each block separately and add their log densities. The target still couples the optimization problems, so the best choice for one factor depends on the others. **MFVI chooses the family; [CAVI](#paper-1) or gradient methods choose its parameters.**

**The cost is lost geometry.** A correlated Gaussian has tilted contours, whereas a product of scalar Gaussians has axis-aligned contours.

<figure class="vi-mfvi-figure">
<img alt="A tilted blue target ellipse compared with a narrower axis-aligned orange mean-field approximation. Both have the same center." src="/assets/vi/mfvi-geometry.svg"/>
<figcaption>Blue: correlated target. Orange: best reverse-KL mean-field fit. The center is correct, but the dependence is missing.</figcaption>
</figure>

For example,

\[
\pi=\mathcal N\!\left(0,\begin{bmatrix}1&\rho\\\rho&1\end{bmatrix}\right),
\qquad
q^\star=\mathcal N\!\left(0,(1-\rho^2)I\right).
\]

The true marginal variances are \(1\), but at \(\rho=0.8\) the fitted variances are \(0.36\). Widening independent factors would put mass outside the narrow tilted region, so reverse KL favors a narrower approximation.

**When it helps.** Mean field offers inexpensive inference when dependencies are weak or speed matters. Strong correlations can make uncertainty too narrow, and separated modes can lead to a fit around just one mode. Larger blocks, [flows](#paper-34), or [hierarchical approximations](#paper-37) can retain more structure.

**What carries forward.** The paper applies mean field to Boltzmann-machine learning. The Gaussian illustration above isolates the same independence tradeoff in a different model. More generally, choosing larger independent blocks preserves dependence inside them. The model's variables need not be independent just because the approximation is.

[Read the source paper](https://wpmedia.wolfram.com/sites/13/2018/02/01-5-6.pdf).
