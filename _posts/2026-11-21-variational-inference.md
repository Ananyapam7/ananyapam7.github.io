---
layout: post
title: "On Variational Inference"
subtitle: "A gentle introduction which will take you up to speed with the current research"
date: 2026-11-21 09:00:00
permalink: /blog/2026/variational-inference/
description: Bayesian updating, normalization, reverse KL, and the evidence lower bound explained with interactive illustrations.
tags: stats bayesian-inference
categories: research
related_posts: false
---

<link rel="stylesheet" href="{{ '/assets/css/vi-explorer.css' | relative_url }}">
<script defer src="{{ '/assets/js/vi-explorer.js' | relative_url }}"></script>
<script defer src="{{ '/assets/js/vi-expectations.js' | relative_url }}"></script>
<script defer src="{{ '/assets/js/vi-kl-comparison.js' | relative_url }}"></script>
<link rel="stylesheet" href="{{ '/assets/css/vi-papers.css' | relative_url }}">
<script defer src="{{ '/assets/js/vi-papers.js' | relative_url }}"></script>
<script defer src="{{ '/assets/js/vi-cavi.js' | relative_url }}"></script>
<script defer src="{{ "/assets/js/vi-svi.js" | relative_url }}"></script>
<script defer src="{{ '/assets/js/vi-research-visuals.js' | relative_url }}"></script>

<div class="vi-intro"><strong>Variational inference and Foundations</strong><p>Start with an observation. Build a target. Fit a distribution.</p><small>Prerequisites: probability densities, expectations, and basic calculus.</small></div>

In Bayesian inference, we start with observed data, <span markdown="0">\(x\)</span>, and quantities we do not know but want to learn about, <span markdown="0">\(z\)</span>. These unknowns might be regression coefficients, missing labels, hidden states, or an entire function. **How should observing <span markdown="0">\(x\)</span> change what we think is plausible about <span markdown="0">\(z\)</span>?**

## What is unknown, and what is a model?

Imagine measuring a quantity with a noisy instrument. We see the readings, but not the underlying value without measurement error. Different underlying values could plausibly have produced the same readings. Reporting just one guess would hide that uncertainty.

A **statistical model** specifies a collection of possible probability distributions for the observations. A **Bayesian model** also describes uncertainty about the unknown quantities, giving a joint probability model for the observations and unknowns. This makes our assumptions explicit: how readings vary around an underlying value, for example, and whether measurement errors are independent.

A probability distribution lets us assign different amounts of plausibility to different possibilities and calculate the probability that an unknown lies in a given range. Treating an unknown parameter probabilistically does not mean its physical value must fluctuate; the distribution represents uncertainty about it. For a continuous quantity, probabilities are areas under a density, rather than the height of the density at a single point.

For now, we take the model as given. We use <span markdown="0">\(z\)</span> for the quantities whose posterior we want to approximate.

| Symbol | Meaning in this article |
| --- | --- |
| <span markdown="0">\(x\)</span> | The observed data, held fixed once observed |
| <span markdown="0">\(z\)</span> | All quantities we want to infer probabilistically |
| <span markdown="0">\(\theta\)</span> | Settings of the given model, held fixed for now |
| <span markdown="0">\(\phi\)</span> | Parameters of a variational approximation, introduced later |

For example, <span markdown="0">\(z\)</span> might contain regression coefficients we want to infer, while <span markdown="0">\(\theta\)</span> specifies a known measurement-noise level.

## How a Bayesian model turns observations into an update

We need two ingredients. A **prior distribution**, <span markdown="0">\(p_\theta(z)\)</span>, describes uncertainty about <span markdown="0">\(z\)</span> before conditioning on the observed data. A **sampling distribution**, <span markdown="0">\(p_\theta(x\mid z)\)</span>, describes how observations could vary for a given <span markdown="0">\(z\)</span>, under the fixed settings <span markdown="0">\(\theta\)</span>.

Before observing data, the sampling distribution is a distribution over possible observations. After we observe <span markdown="0">\(x\)</span>, we hold it fixed and view the same expression as a function of <span markdown="0">\(z\)</span>. In that role, it is called the **likelihood**. A likelihood is not generally a probability distribution over the unknown quantities.

Return to the noisy instrument. For each possible true value, ask how compatible it is with the reading we observed. The likelihood gives more weight to values that make that reading plausible and less weight to values that make it surprising. Multiplying by the prior reweights our initial uncertainty using this compatibility with the data. Normalization then turns the resulting weights into a probability distribution.

Those two ingredients specify one joint distribution. The probability product rule lets us write it in two ways:

<div markdown="0">
\[
p_\theta(x,z)
=
\underbrace{p_\theta(z)\,p_\theta(x\mid z)}_{\text{prior and sampling model}}
=
\underbrace{p_\theta(x)\,p_\theta(z\mid x)}_{\text{evidence and posterior}}.
\]
</div>

Rearranging gives Bayes’ rule. The **posterior** <span markdown="0">\(p_\theta(z\mid x)\)</span> is the updated distribution over <span markdown="0">\(z\)</span>, obtained by multiplying the prior by the likelihood and dividing by the **evidence** <span markdown="0">\(p_\theta(x)\)</span>.



For the interactive example, let the prior be <span markdown="0">\(z\sim\mathcal N(0,1)\)</span> and the observation model be <span markdown="0">\(x\mid z\sim\mathcal N(z,0.8^2)\)</span>. Completing the square gives

<div markdown="0">
\[z\mid x\sim\mathcal N\!\left(\frac{x}{1+0.8^2},\frac{0.8^2}{1+0.8^2}\right).\]
</div>

The posterior mean lies between the prior mean and the observation. Its variance is smaller than the prior variance. Moving the observation changes the center; the fixed observation noise keeps the posterior spread constant.

{% include vi-explorer.html kind='update' %}



*Figure 1. The prior and likelihood are functions of the same <span markdown="0">\(z\)</span>. Multiply them pointwise, then rescale the product to have area one. In this illustration, the posterior shifts toward the values favored by the data.*

The joint notation works across models because it leaves open what’s inside each factor. In regression, <span markdown="0">\(z\)</span> can be a vector of coefficients and we can condition on known inputs. In a state-space model, <span markdown="0">\(z\)</span> can be a trajectory whose successive states depend on each other. In a mixture model, <span markdown="0">\(z\)</span> can contain both unknown group labels and continuous group parameters. **The update is the same. Only the assumptions that specify the joint probability are different.**

## From Bayesian inference to a more general inference problem

We have seen that Bayesian inference gives us a posterior distribution over the unknown quantities <span markdown="0">\(z\)</span>, conditional on the observed data <span markdown="0">\(x\)</span>. For continuous <span markdown="0">\(z\)</span>, Bayes' rule gives

<div markdown="0">
\[
p_\theta(z\mid x)=\frac{p_\theta(x,z)}{\int p_\theta(x,z')\,dz'}.
\]
</div>

At first glance, this seems to solve our problem: we have an expression for the posterior we wanted. But **writing down a distribution and being able to compute or work with it are different things**.

In many models, evaluating the joint density <span markdown="0">\(p_\theta(x,z)\)</span> at a particular value of <span markdown="0">\(z\)</span> is straightforward. The denominator requires integrating over every possible value. For simple models, this integral may be available analytically. For more complicated models, particularly when the unknowns are high-dimensional and dependent, it can be computationally intractable.

We therefore often know the posterior only up to a proportionality constant:

<div markdown="0">
\[
p_\theta(z\mid x)\propto p_\theta(x,z).
\]
</div>

This suggests a more general formulation. Suppose we are given a nonnegative function <span markdown="0">\(\gamma(z)\)</span>, and we want to work with the probability distribution

<div markdown="0">
\[
\boxed{\pi(z)=\frac{\gamma(z)}{Z},\qquad Z=\int\gamma(z)\,dz.}
\]
</div>

We assume <span markdown="0">\(0\lt Z\lt\infty\)</span>, so the target is well defined. Here, <span markdown="0">\(\gamma\)</span> is the **unnormalized density**, <span markdown="0">\(\pi\)</span> is the **normalized target density**, and <span markdown="0">\(Z\)</span> is the **normalizing constant**. For discrete variables, we replace the integral with a sum.

The Bayesian case fits this notation exactly:

<div markdown="0">
\[
\gamma(z)=p_\theta(x,z),\qquad
\pi(z)=p_\theta(z\mid x),\qquad
Z=p_\theta(x).
\]
</div>

Computing a Bayesian posterior is thus one instance of the broader problem of working with a probability distribution specified only up to normalization.

### Why is this formulation more general?

The function <span markdown="0">\(\gamma\)</span> need not come from a prior and a likelihood.

In **statistical physics**, we may start with an energy function <span markdown="0">\(U(z)\)</span> for a system in state <span markdown="0">\(z\)</span>. Its Boltzmann distribution at temperature <span markdown="0">\(T>0\)</span>, in units where Boltzmann's constant is one, is

<div markdown="0">
\[
\pi(z)=\frac{\exp[-U(z)/T]}{Z}.
\]
</div>

Here, <span markdown="0">\(\gamma(z)=\exp[-U(z)/T]\)</span>. We do not need an observed dataset or a Bayesian posterior to define this target.

In an **energy-based model**, an energy function <span markdown="0">\(U_\theta(z)\)</span> similarly assigns relative plausibility to configurations:

<div markdown="0">
\[
\pi_\theta(z)=\frac{\exp[-U_\theta(z)]}{Z_\theta}.
\]
</div>

Lower energy means higher density relative to other configurations.

A **Gibbs-type distribution** can instead combine a reference density <span markdown="0">\(p_0(z)\)</span> and a loss function <span markdown="0">\(R(z)\)</span>:

<div markdown="0">
\[
\pi(z)=\frac{p_0(z)\exp[-\lambda R(z)]}{Z},\qquad\lambda>0.
\]
</div>

Values with smaller loss receive more weight relative to the reference density. The loss need not arise from a likelihood.

These constructions start with different objects: a joint density, an energy function, or a loss. Yet each leads to a target of the form <span markdown="0">\(\pi\propto\gamma\)</span>. **This separates defining the probability distribution from performing inference with it.**

{% include vi-explorer.html kind='scale' %}

*Figure 2. Multiplying <span markdown="0">\(\gamma\)</span> by a positive constant changes its height and total area by the same factor. After normalization, the target <span markdown="0">\(\pi\)</span> remains unchanged.*

## How can we solve the inference problem?

We can evaluate <span markdown="0">\(\gamma\)</span>, perhaps only up to a multiplicative constant, and want to characterize the corresponding target <span markdown="0">\(\pi=\gamma/Z\)</span>. Depending on the problem, this might mean obtaining its density, drawing samples from it, or constructing a tractable approximation to it. **These are different kinds of answers to the same underlying inference problem.**

Even knowing <span markdown="0">\(Z\)</span> does not necessarily make integration, marginalization, or sampling easy. Evaluating a density pointwise and performing inference with it are different tasks; the structure of the target determines which methods are practical.

<details class="vi-mcmc-note" markdown="1">
<summary>Why knowing the normalizing constant is not enough</summary>

Even if the normalizing constant <span markdown="0">\(Z\)</span> were known, working with the resulting distribution could still be difficult. **Knowing the density at any point is not the same as being able to calculate how much probability lies in a whole region.** This distinction becomes particularly important when <span markdown="0">\(z\)</span> is high-dimensional.

Suppose we know <span markdown="0">\(Z\)</span> exactly and can evaluate <span markdown="0">\(\gamma(z)\)</span>. Then we can evaluate <span markdown="0">\(\pi(z)=\gamma(z)/Z\)</span> at any chosen point: the normalization problem is solved. But an event probability and a marginal density still require integration:

<div markdown="0">
\[
\Pr_\pi(z\in B)=\int_B\pi(z)\,dz,
\qquad
\pi_1(z_1)=\int_{\mathbb R^{d-1}}\pi(z_1,z_2,\ldots,z_d)\,dz_2\cdots dz_d.
\]
</div>

Here <span markdown="0">\(B\)</span> is a region of the state space, and <span markdown="0">\(\pi_1\)</span> is the marginal density of the first coordinate. Computing means and covariances also requires integrals.

**A concrete example.** Consider the target on <span markdown="0">\(\mathbb R^d\)</span>

<div markdown="0">
\[
\pi(z)=\frac1Z\exp\!\left(-\frac12 z^\top A z-\lambda\sum_{i=1}^d z_i^4\right),
\qquad A=A^\top\succ0,\quad\lambda>0.
\]
</div>

Suppose someone gives us its exact value. Evaluating the density at a chosen vector <span markdown="0">\(z\)</span> is now straightforward. Yet the marginal density of <span markdown="0">\(z_1\)</span> is

<div markdown="0">
\[
\pi_1(z_1)=\frac1Z\int_{\mathbb R^{d-1}}
\exp\!\left(-\frac12 z^\top A z-\lambda\sum_{i=1}^d z_i^4\right)
\,dz_2\cdots dz_d.
\]
</div>

For each fixed <span markdown="0">\(z_1\)</span>, this is still a <span markdown="0">\((d-1)\)</span>-dimensional integral. The off-diagonal entries of <span markdown="0">\(A\)</span> create cross terms because

<div markdown="0">
\[
z^\top A z=\sum_{i=1}^d A_{ii}z_i^2+2\sum_{i\lt j}A_{ij}z_i z_j.
\]
</div>

For a general dense <span markdown="0">\(A\)</span>, these terms couple the coordinates, so the integrand does not factor into a product of one-dimensional functions. It gives us the value of one particular integral over the whole space, not all the partial integrals needed for marginals or event probabilities.

**Sampling is a separate problem too.** Even if a univariate density is normalized and easy to evaluate, generating a random draw requires a procedure. Inverse-transform sampling provides a theoretical construction:

<div markdown="0">
\[
F(t)=\int_{-\infty}^{t}\pi(u)\,du,
\qquad z^\star=F^{-1}(U),\quad U\sim\operatorname{Uniform}(0,1).
\]
</div>

Constructing the CDF already requires integration, and evaluating its inverse may require numerical work. Sampling becomes harder in higher dimensions. This is why rejection sampling and MCMC can be useful even for a normalized target.

Some distributions are easier because of their mathematical form. For <span markdown="0">\(\pi(z)=\mathcal N(z;\mu,\Sigma)\)</span>, with positive-definite <span markdown="0">\(\Sigma\)</span>, the Gaussian structure gives us moments, marginals, and conditionals, as well as a sampling construction: if <span markdown="0">\(LL^\top=\Sigma\)</span> and <span markdown="0">\(\varepsilon\sim\mathcal N(0,I)\)</span>, then <span markdown="0">\(z^\star=\mu+L\varepsilon\)</span> has the target distribution. This tractability comes from the Gaussian family, not simply from knowing its normalizing constant.

<div markdown="0">
\[
\boxed{\text{Evaluating a density}\;\neq\;\text{performing inference with it}.}
\]
</div>

The broader problem is therefore how to work with a distribution that may be easy to evaluate pointwise but difficult to integrate, marginalize, or sample from efficiently. Exact methods, Monte Carlo methods, and variational inference address different aspects of this problem.

</details>

<details class="vi-mcmc-note" markdown="1">
<summary>Exact inference</summary>

Some models allow an analytic answer. For example, a Beta prior for a Bernoulli success probability gives a Beta posterior after observing successes and failures. The Gaussian update above is another example: we obtained the posterior mean and variance directly.

</details>

<details class="vi-mcmc-note" markdown="1">
<summary>Numerical integration and direct sampling</summary>

When symbolic calculations are unavailable, numerical integration can approximate the needed integrals. Quadrature can be effective in low dimensions, although the cost of straightforward grid-based methods grows rapidly with dimension.

Alternatively, we may be able to generate independent samples from the target. Rejection sampling is one option if we have a proposal density we can sample from and a suitable bound on the unnormalized target relative to that proposal. It can avoid evaluating <span markdown="0">\(Z\)</span>, but finding a useful bound and achieving a reasonable acceptance rate may be difficult.

</details>

<details class="vi-mcmc-note" markdown="1">
<summary>Markov chain Monte Carlo (MCMC)</summary>

**MCMC** constructs a Markov chain with <span markdown="0">\(\pi\)</span> as its stationary distribution. It does not generally compute <span markdown="0">\(Z\)</span>, provide an explicit normalized density, or produce independent draws.

Target-density ratios cancel the unknown normalizing constant, which lets methods such as Metropolis-Hastings construct transitions without evaluating it. Under suitable convergence conditions, the chain approaches the target distribution. Finite runs can explore slowly, and successive samples are generally correlated.

<details class="vi-mcmc-note" markdown="1">
<summary>How do MCMC samples answer questions about the target?</summary>

For a function <span markdown="0">\(f\)</span>, the expectation <span markdown="0">\(\mathbb E_\pi[f(z)]\)</span> is its probability-weighted average. A well-mixing chain lets us estimate it by averaging over its samples:

<div markdown="0">
\[
\mathbb E_\pi[f(z)]\approx\frac1N\sum_{n=1}^N f(z^{(n)}).
\]
</div>

Choosing <span markdown="0">\(f(z)=z\)</span> estimates a mean; choosing <span markdown="0">\(f(z)=\mathbf 1_A(z)\)</span> estimates an event probability; choosing <span markdown="0">\(f(z)=z^2\)</span> estimates a second moment. The indicator is one inside <span markdown="0">\(A\)</span> and zero outside it. For scalar <span markdown="0">\(z\)</span>, the variance is <span markdown="0">\(\mathbb E_\pi[z^2]-(\mathbb E_\pi[z])^2\)</span>.

{% include vi-expectations.html %}

The visual shows exact Gaussian expectations, not a simulated MCMC run. The density stays fixed while the function being averaged changes. The second moment equals the variance here only because the mean is zero.

</details>

</details>

## Variational inference

**Variational inference (VI)** introduces a family of tractable distributions <span markdown="0">\(q_\phi(z)\)</span>, indexed by parameters <span markdown="0">\(\phi\)</span>, and fits a member of that family to the target:

<div markdown="0">
\[
q_{\phi^\star}(z)\approx\pi(z).
\]
</div>

For example, suppose we allow only Gaussian approximations, <span markdown="0">\(q_\phi(z)=\mathcal N(z;m,s^2)\)</span>, with <span markdown="0">\(\phi=(m,s)\)</span> and <span markdown="0">\(s>0\)</span>. We can move the center and change the spread, but every candidate remains Gaussian. The parameters <span markdown="0">\(\phi\)</span> are the controls for those adjustments; fitting the approximation means choosing their settings. This family is tractable because we can evaluate its density and generate samples easily.

A single Gaussian cannot reproduce every target: it cannot match two separated peaks exactly, however carefully we adjust its center and spread. Choosing the family determines which shapes are available; optimization chooses among those shapes.

The result is a fitted distribution that we can use to describe uncertainty and calculate or estimate quantities of interest. Its accuracy depends on both what the family can represent and how well we optimize within it.

What does it mean for one distribution to approximate another well? We need a criterion that compares their probability assignments, and a family in which we can optimize that criterion.

A common choice is **reverse Kullback-Leibler divergence**:

<div markdown="0">
\[
\mathrm{KL}(q_\phi\|\pi)
=\int q_\phi(z)\log\frac{q_\phi(z)}{\pi(z)}\,dz
=\mathbb E_{q_\phi}[\log q_\phi(z)-\log\pi(z)].
\]
</div>

Imagine drawing values from our current approximation. At each draw, compare the density assigned by the approximation with the density assigned by the target, using their log ratio. Reverse KL averages this comparison over the places the approximation itself visits. Changing the direction of KL changes whose draws we average over.

KL is nonnegative and is zero when the two distributions match. It is not a symmetric distance: exchanging <span markdown="0">\(q_\phi\)</span> and <span markdown="0">\(\pi\)</span> changes the criterion.

Why this direction? The expectation is taken under our own approximation, which we choose to make tractable. We can often sample from <span markdown="0">\(q_\phi\)</span> and evaluate its density even when we cannot directly sample from <span markdown="0">\(\pi\)</span>. The criterion also strongly penalizes putting mass where the target has very little density. Other divergence criteria are possible, and this choice affects which approximation is preferred.

<details class="vi-mcmc-note" markdown="1">
<summary>Why can reverse KL favor just one of two peaks?</summary>

The two animations show a two-dimensional target with two separated modes. Blue contours stay fixed; the red Gaussian approximation moves and changes shape. Forward KL stretches the red contours across both modes, while reverse KL tightens them around one.

For a precise description, write the target in coordinates <span markdown="0">\(w=(u,v)\)</span>:

<div markdown="0">
\[
\pi_w(u,v)=\left[\tfrac12\mathcal N(u;-3,0.6^2)+\tfrac12\mathcal N(u;3,0.6^2)\right]\mathcal N(v;0,0.8^2),
\]
\[
q_w(u,v)=\mathcal N(u;m_u,s_u^2)\mathcal N(v;m_v,s_v^2).
\]
</div>

The plots rotate both distributions by 25 degrees, <span markdown="0">\(z=Rw\)</span>, to place the modes diagonally. This shared rotation changes neither KL objective. Both runs start at <span markdown="0">\((m_u,m_v)=(1.2,-1)\)</span> and <span markdown="0">\((s_u,s_v)=(1.3,1.8)\)</span>. Only the direction of KL changes:

<div markdown="0">
\[
\underbrace{\mathrm{KL}(\pi\|q)=\mathbb E_\pi[\log\pi-\log q]}_{\text{forward KL: average over the target}},
\qquad
\underbrace{\mathrm{KL}(q\|\pi)=\mathbb E_q[\log q-\log\pi]}_{\text{reverse KL: average over the approximation}}.
\]
</div>

{% include vi-kl-comparison.html %}

**Forward KL asks whether the approximation covers places the target visits.** The target visits both peaks. A narrow Gaussian on one peak would assign extremely small density to draws from the other, producing a large penalty. The fitted Gaussian therefore broadens to cover both. For this target, the forward-KL optimum matches its mean and covariance: in the unrotated coordinates, <span markdown="0">\((m_u,m_v)=(0,0)\)</span> and <span markdown="0">\((s_u^2,s_v^2)=(9.36,0.64)\)</span>. It covers both peaks, but also puts substantial probability in the valley: a single Gaussian cannot reproduce the target's two-peak shape.

**Reverse KL asks whether the places the approximation visits are plausible under the target.** A broad Gaussian visits the valley between the peaks, where the target density is tiny. Narrowing around one peak avoids those visits. Once the approximation concentrates there, it rarely visits the other peak, which receives little direct weight in the expectation. Here the run settles near <span markdown="0">\((m_u,m_v)=(3,0)\)</span> and <span markdown="0">\((s_u,s_v)=(0.6,0.8)\)</span>, matching the upper-right component after rotation.

The target is symmetric, but the starting approximation is offset toward the positive-u mode. That offset selects the upper-right solution in this run; reflecting the initial u-coordinate would select the other mode. The available shapes matter too: a family with two Gaussian components can represent this particular target exactly.

The loss plots show improvement within each run. Their numerical values measure different objectives and should not be compared as a single ranking of the two fits.

</details>

With a chosen family and criterion, we seek

<div markdown="0">
\[
\phi^\star\in\operatorname*{arg\,min}_\phi\mathrm{KL}(q_\phi\|\pi).
\]
</div>

In practice, optimization may find a local optimum.

There is an apparent obstacle: the objective contains <span markdown="0">\(\pi\)</span>, whose normalizing constant may be unknown. But substituting <span markdown="0">\(\pi=\gamma/Z\)</span> turns that unknown scale into an additive <span markdown="0">\(\log Z\)</span>. **For a fixed target, this term is the same for every candidate, so it does not affect which variational parameters optimize the objective.** Computing the numerical KL value and optimizing it are therefore different requirements.

Let us make that cancellation explicit, one step at a time.


### From reverse KL to the ELBO

Keep the target fixed while we vary <span markdown="0">\(\phi\)</span>, with <span markdown="0">\(q_\phi\)</span> a normalized density.

Start with the reverse KL we want to minimize:

<div markdown="0">
\[
\mathrm{KL}(q_\phi\|\pi)
=\mathbb E_{q_\phi}\!\left[\log q_\phi(z)-\log\pi(z)\right].
\]
</div>

Because <span markdown="0">\(\pi(z)=\gamma(z)/Z\)</span>, we have <span markdown="0">\(\log\pi(z)=\log\gamma(z)-\log Z\)</span>. Substituting, and keeping track of the minus sign, gives

<div markdown="0">
\[
\mathrm{KL}(q_\phi\|\pi)
=\mathbb E_{q_\phi}\!\left[\log q_\phi(z)-\log\gamma(z)+\log Z\right].
\]
</div>

The logarithm has turned the unknown multiplicative scale into an additive term. We have not computed <span markdown="0">\(Z\)</span>; we have isolated where it enters the objective.

For this fixed target, <span markdown="0">\(\log Z\)</span> does not depend on <span markdown="0">\(z\)</span>. Since <span markdown="0">\(q_\phi\)</span> integrates to one,

<div markdown="0">
\[
\mathbb E_{q_\phi}[\log Z]
=\log Z\int q_\phi(z)\,dz
=\log Z.
\]
</div>

So, even though the averaging distribution changes with <span markdown="0">\(\phi\)</span>, this particular expectation stays constant. We obtain

<div markdown="0">
\[
\mathrm{KL}(q_\phi\|\pi)
=\log Z+\mathbb E_{q_\phi}[\log q_\phi(z)-\log\gamma(z)].
\]
</div>

Reverse the signs inside the remaining expectation and define

<div markdown="0">
\[
\boxed{\mathcal L(\phi)
=\mathbb E_{q_\phi}[\log\gamma(z)-\log q_\phi(z)].}
\]
</div>

There is also an intuitive way to read these two terms:

<div markdown="0">
\[
\mathcal L(\phi)=\underbrace{\mathbb E_{q_\phi}[\log\gamma(z)]}_{\text{favor high target density}}
+\underbrace{\mathcal H(q_\phi)}_{\text{retain spread}},
\qquad \mathcal H(q_\phi)=-\mathbb E_{q_\phi}[\log q_\phi(z)].
\]
</div>

The first term rewards putting probability in regions where the target density is high. The entropy term rewards retaining spread. Together, they balance concentrating in plausible regions with representing uncertainty, rather than simply selecting one high-density point. Spreading out indiscriminately is not rewarded overall: it can move probability into regions with low target density and worsen the first term.

<details class="vi-mcmc-note" markdown="1">
<summary>A note on entropy for continuous distributions</summary>

For continuous distributions, <span markdown="0">\(\mathcal H\)</span> is called differential entropy. For a Gaussian, <span markdown="0">\(\mathcal H(\mathcal N(m,s^2))=\tfrac12\log(2\pi e s^2)\)</span>, so increasing its spread increases its entropy. Shrinking its spread to zero drives that entropy to minus infinity.

</details>

This quantity is the **evidence lower bound**, or **ELBO**, when our target is a Bayesian posterior. The same objective also applies to a general unnormalized target. Substitution gives the central identity:

<div markdown="0">
\[
\boxed{\log Z=\mathcal L(\phi)+\mathrm{KL}(q_\phi\|\pi).}
\]
</div>

Notice what the ELBO requires: evaluations of <span markdown="0">\(\log\gamma\)</span>, evaluations of <span markdown="0">\(\log q_\phi\)</span>, and an expectation under <span markdown="0">\(q_\phi\)</span>. It does not require the value of <span markdown="0">\(Z\)</span>.

For a fixed target, <span markdown="0">\(\log Z\)</span> is a fixed level. The ELBO sits below it, and the distance between them is exactly the reverse KL. If we raise the ELBO by one unit, the KL falls by one unit:

<div markdown="0">
\[
\mathcal L(\phi_2)-\mathcal L(\phi_1)
=\mathrm{KL}(q_{\phi_1}\|\pi)-\mathrm{KL}(q_{\phi_2}\|\pi).
\]
</div>

Therefore the same parameters solve both optimization problems:

<div markdown="0">
\[
\operatorname*{arg\,max}_{\phi}\mathcal L(\phi)
=\operatorname*{arg\,min}_{\phi}\mathrm{KL}(q_\phi\|\pi).
\]
</div>

**We do not need to know the height of the fixed level to move toward it.** Comparing ELBO values is enough to tell which candidate has the smaller reverse KL.

{% include vi-explorer.html kind='fit' %}

KL divergence is nonnegative, so the identity immediately implies

<div markdown="0">
\[
\mathcal L(\phi)\leq\log Z.
\]
</div>

In the Bayesian case, <span markdown="0">\(\gamma(z)=p_\theta(x,z)\)</span> and <span markdown="0">\(Z=p_\theta(x)\)</span>. Consequently,

<div markdown="0">
\[
\mathcal L(\phi)
=\mathbb E_{q_\phi}[\log p_\theta(x,z)-\log q_\phi(z)]
\leq\log p_\theta(x).
\]
</div>

The ELBO is thus a lower bound on the **log evidence**. Equality holds when <span markdown="0">\(q_\phi\)</span> matches the posterior. If the variational family cannot represent the posterior, even its best member leaves a gap. An imperfect optimization procedure can leave an additional gap.

We have now transformed the original inference problem into an optimization problem:

<div markdown="0">
\[
\phi^\star\in\arg\max_\phi\mathcal L(\phi).
\]
</div>

But this does not mean that the problem is solved. Depending on the target distribution and the variational family, evaluating the ELBO, calculating its derivatives, and finding its optimum may still be computationally difficult.

This is where variational inference algorithms begin to diverge. Some exploit conditional independence or conjugacy in the probabilistic model. Others exploit the structure of the variational family, identities for differentiating expectations, or techniques for reducing the variance of stochastic gradients.

The question guiding the rest of this article is therefore: **What mathematical structure does each method exploit, what does it change, and which difficulty does that change resolve?**

## A connected reading of variational inference

Each entry makes two things explicit: **the setup it assumes** and **the contribution it makes**. A factorization of the model describes how the unknowns and observations depend on one another. A factorization of <span markdown="0">\(q_\phi\)</span> describes the approximation we choose. These are different decisions.

From there, a paper may change the approximation family, the objective, the gradient estimator, or the optimization procedure. Others analyze an existing method's error or convergence. Keeping these distinctions separate lets us see which ideas can be combined: a richer family can use a better gradient estimator without changing the target. Follow the questions below, or the connections beside each paper.

We keep <span markdown="0">\(x\)</span> for observations, <span markdown="0">\(z\)</span> for unknowns, <span markdown="0">\(\theta\)</span> for model parameters, and <span markdown="0">\(\phi\)</span> for approximation parameters. Throughout,

<div markdown="0">
\[
\pi(z)=\frac{\gamma(z)}{Z},\qquad
w_\phi(z)=\frac{\gamma(z)}{q_\phi(z)},\qquad
\mathcal L(\phi)=\mathbb E_{q_\phi}[\log w_\phi(z)].
\]
</div>

The **importance weight** <span markdown="0">\(w_\phi\)</span> compares the unnormalized target with the approximation at a sampled point. It will connect ordinary VI to several alternative objectives. In the notes, <span markdown="0">\(q\)</span> and <span markdown="0">\(w\)</span> abbreviate <span markdown="0">\(q_\phi\)</span> and <span markdown="0">\(w_\phi\)</span>; <span markdown="0">\(\epsilon\sim\nu\)</span> denotes base noise, and <span markdown="0">\(\widehat g_\phi\)</span> a sampled gradient. Each new symbol is introduced where it is needed.

When a paper learns the model as well as the approximation, we write the Bayesian specialization <span markdown="0">\(\gamma(z)=p_\theta(x,z)\)</span>. An inference update varies <span markdown="0">\(\phi\)</span> while holding <span markdown="0">\(\theta\)</span> fixed.

<details class="vi-mcmc-note" markdown="1">
<summary>Shared notation for the paper notes</summary>

<span markdown="0">\(q_j=q_{\phi_j}\)</span> denotes a factor, and <span markdown="0">\(q_{-j}=\prod_{k\ne j}q_k\)</span> the remaining factors. Parenthesized superscripts mark optimization iterates: <span markdown="0">\(q^{(t)}\)</span> and <span markdown="0">\(\phi^{(t)}\)</span>. A star denotes an optimum; a hat denotes an estimate.

Samples are <span markdown="0">\(z^{(s)}\)</span>, with importance weights <span markdown="0">\(w_s=w_\phi(z^{(s)})\)</span> and normalized weights <span markdown="0">\(\bar w_s=w_s/\sum_r w_r\)</span>. We use <span markdown="0">\(K\)</span> for the number of Monte Carlo draws, <span markdown="0">\(N\)</span> for observations, and <span markdown="0">\(d\)</span> for dimension.

<span markdown="0">\(\mathcal L[q]\)</span> views the ELBO as a functional of a distribution; <span markdown="0">\(\mathcal L(\phi)=\mathcal L[q_\phi]\)</span> views the same quantity as a function of its parameters. Gaussian factors use mean <span markdown="0">\(m_j\)</span>, standard deviation <span markdown="0">\(s_j\)</span>, and variance <span markdown="0">\(v_j=s_j^2\)</span>. Optimization step sizes are <span markdown="0">\(\eta_t\)</span>; <span markdown="0">\(\rho\)</span> denotes correlation. Additional parameters for a learned control variate use <span markdown="0">\(\psi\)</span>.

</details>

{% include vi-papers.html %}
