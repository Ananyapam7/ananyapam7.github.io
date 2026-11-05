---
layout: page
title: Score Correction
description: Making protein profile searches more reliable by accounting for gaps and learning from false-positive matches.
img: assets/img/score-correction/thumbnail.png
importance: 4
category: Major
---

A protein search should give a high score to a biologically meaningful match. But some regions of a sequence profile can produce convincing scores for the wrong reasons: an alignment may be repeatedly interrupted by gaps, or a few profile columns may match unrelated sequences unusually well.

In this project, we explored two ways to adjust the scores used by **MMseqs2**. Both act on individual profile columns, so the existing search machinery can use the corrected scores.

| Problem | Information used | Correction |
| --- | --- | --- |
| Repeatedly interrupted alignment regions | Local patterns of residues and gaps | Reduce scores in persistently gappy regions |
| Unrelated sequences receive unexpectedly high scores | Matches to reversed or scrambled sequences | Adjust the columns responsible for those matches |

## First, what is a sequence profile?

Proteins are written as strings of amino-acid letters. When several related proteins are aligned, comparable positions line up in columns. A dash, `-`, marks a gap: a position without an aligned residue in that sequence. This is a **multiple sequence alignment**, or **MSA**.

A **profile** summarizes the amino-acid preferences at each column. It gives a residue a favorable score when that residue is more common in the profile than it would be by background chance. An alignment score combines these column scores with gap costs.

MMseqs2 uses profile scores both to find promising short-word matches in its **k-mer prefilter** and to evaluate candidates with **Smith–Waterman alignment**. This is why changing the profile itself can affect both search stages. See the [MMseqs2 user guide](https://github.com/soedinglab/MMseqs2/wiki#overview-of-important-mmseqs2-modules) for the search pipeline.

## 1. Use gap structure to identify unreliable regions

### Missing coverage and repeated interruptions are different

A high fraction of gap characters does not necessarily mean an alignment is unreliable. Imagine 100 sequences, of which 99 start only at column 51. The first 50 columns contain 99% gaps, but the one sequence observed there is uninterrupted.

That situation is different from a region where sequences repeatedly switch between residues and gaps. We wanted to reduce the influence of the second pattern without automatically penalizing the first.

{% include figure.html path="assets/img/score-correction/alignment-windows.png" class="img-fluid" alt="Two toy multiple sequence alignments with identical gap counts. On the left, five sequences have a missing prefix; on the right, those gaps interrupt the sequences repeatedly. Blue rectangles mark five-column windows." caption="Toy alignments with the same overall gap fraction. In the highlighted window, rows containing only gaps are excluded from the local calculation. The observed fragment on the left is continuous; most observed rows on the right are interrupted." zoomable=true %}

### Measure continuity within a short window

For each column, take a window around it—for example, **15 columns**, with seven on either side. Among the sequences that have **at least one residue** in that window, ask:

> What fraction pass through the entire window without a gap?

Call this fraction **f**. A value of 1 means all observed sequences are uninterrupted; a value near 0 means almost all observed sequences contain a gap. Sequence weights prevent a large number of nearly identical sequences from dominating the calculation.

We turn this into a **negative score adjustment**. With a smoothing constant of β = 1/3:

| Uninterrupted fraction, f | Score adjustment |
| --- | --- |
| 100% | 0 bits |
| 50% | −0.68 bits |
| 25% | −1.19 bits |
| 0.1% | approximately −2.00 bits |

A more negative adjustment means a larger reduction in the match score. The parameter β controls its strength and keeps the adjustment finite when f is zero.

### Avoid penalizing the start of a fragment

A window that straddles the start of many sequences looks interrupted, even if each sequence is continuous once it begins. Applying the raw window adjustment would create an artificial dip in scores around that boundary.

We therefore examine **all windows containing a column** and use the **least severe adjustment** among them. A clean overlapping window can explain an isolated fragment boundary. In a persistently interrupted region, all nearby windows remain gappy, so a reduction remains.

{% include figure.html path="assets/img/score-correction/boundary-correction.png" class="img-fluid" alt="Toy score-adjustment curves. At a single fragment boundary, the local negative dip disappears after selecting the least severe overlapping window. With repeated internal gaps, the negative adjustment remains." caption="The same toy alignments, with five-column windows and β = 1/3. The correction removes a boundary artifact while retaining a penalty for repeated interruptions. These curves illustrate the rule, rather than benchmark performance." zoomable=true %}

<details class="technical-note" markdown="1">
<summary>The window formula and the sign of the correction</summary>

Let the window centered at column i contain W = 2D + 1 columns, and let wₙ be the weight of sequence n. Then

<div markdown="0">
\[
f_i =
\frac{\sum_n w_n\,\mathbf{1}\{x_n[i-D:i+D]\text{ has no gaps}\}}
{\sum_n w_n\,\mathbf{1}\{x_n[i-D:i+D]\text{ has at least one residue}\}}.
\]
</div>

Write the adjustment added to the profile as

<div markdown="0">
\[
g_i = \log_2\!\left(\frac{\beta+f_i}{\beta+1}\right) \leq 0,
\qquad
\Delta S_i = \max_{j:\,|j-i|\leq D} g_j.
\]
</div>

The maximum is intentional: **among negative numbers, the maximum is the least severe reduction**. Equivalently, if a penalty magnitude is defined as Pᵢ = −gᵢ ≥ 0, the adjustment is the negative of the minimum overlapping penalty magnitude. Mixing these two sign conventions would reverse the boundary correction.

The original formulation also included an empirical offset:

<div markdown="0">
\[
\Delta S_i = \max_{j:\,|j-i|\leq D} g_j + A + B N_{\mathrm{eff}}.
\]
</div>

Here Nₑff summarizes the effective number of sequences in the relevant region. The constants β, D, A, and B should be tuned on validation data separate from the final test set. For example, D = 7 gives W = 15; D = 15 gives W = 31.

</details>

## 2. Learn which profile columns produce false positives

Gap structure is only one source of misleading scores. Some profiles also give unusually high scores to unrelated sequences. During an iterative search, a false positive can be incorporated into the next profile and influence later searches.

The second approach uses **decoy sequences as negative controls**. Reversing or scrambling sequences disrupts their biological order while retaining properties such as amino-acid composition. A decoy that scores unusually well identifies a region of the profile worth correcting.

An **E-value** is the expected number of chance matches at least as strong as a reported match, under the search's statistical model. It is not the probability that a particular match is false. We use the score corresponding to **E = 1** as a diagnostic cutoff for decoys.

### The correction loop

<div class="row my-4" role="list" aria-label="Decoy-based score correction workflow">
  <div class="col-md-6 mb-3" role="listitem">
    <div class="border rounded p-3 h-100">
      <p class="mb-1"><strong>1. Search real sequences and decoys</strong></p>
      <p class="mb-0">Use the current query profile against the target database and its decoy counterpart.</p>
    </div>
  </div>
  <div class="col-md-6 mb-3" role="listitem">
    <div class="border rounded p-3 h-100">
      <p class="mb-1"><strong>2. Inspect high-scoring decoys</strong></p>
      <p class="mb-0">Find decoy matches with E-values below 1 and trace their scores back to profile columns.</p>
    </div>
  </div>
  <div class="col-md-6 mb-3" role="listitem">
    <div class="border rounded p-3 h-100">
      <p class="mb-1"><strong>3. Adjust the responsible columns</strong></p>
      <p class="mb-0">Give more weight to decoys that exceed the cutoff by a larger margin.</p>
    </div>
  </div>
  <div class="col-md-6 mb-3" role="listitem">
    <div class="border rounded p-3 h-100">
      <p class="mb-1"><strong>4. Carry the correction forward</strong></p>
      <p class="mb-0">Build the next profile from real-sequence matches, retaining the accumulated score correction before searching again.</p>
    </div>
  </div>
</div>

This targets columns that contribute strongly favorable scores to spurious matches. It aims to reduce those matches while retaining the profile's ability to recognize homologous sequences.

### A small numerical example

Suppose a decoy receives **40 bits**, but the cutoff corresponding to E = 1 is **24 bits**. The excess is 16 bits, or **40% of the decoy's score**. In a simple additive example, removing 40% of each column's contribution brings the total to 24 bits.

{% include figure.html path="assets/img/score-correction/decoy-example.png" class="img-fluid" alt="An illustrative six-column decoy alignment. Contributions of 4, 7, 10, 9, 6, and 4 bits total 40. Reducing each by 40 percent gives 24 bits in total." caption="Illustrative arithmetic for one fixed alignment with no gap costs. The cutoff motivates the weighting rule; this is not a measured benchmark result. Real gapped alignments need not land exactly at the cutoff after correction." zoomable=true %}

With multiple decoys, a column receives the largest weighted contribution among the eligible decoy matches covering it. Corrections accumulate over successive iterations. The same approach can also be applied after a profile has already been constructed, using a separate decoy search.

<details class="technical-note" markdown="1">
<summary>The decoy update and its assumptions</summary>

Let Sₘ be a decoy's alignment score and S₀ the score corresponding to E = 1 for the real target database. For positive scores with Sₘ > S₀, define

<div markdown="0">
\[
\alpha_m = \frac{S_m-S_0}{S_m}.
\]
</div>

This weight is small for a decoy just above the cutoff and approaches 1 for a much stronger decoy. Let ℓₜ₋₁(a, i) be the current query profile's score for amino acid a at column i, and let aₘᵢ denote the decoy residue aligned to that column. The proposed update is

<div markdown="0">
\[
\delta c_t(i) =
\max_{\substack{m:\,S_m>S_0\\i\text{ covered by decoy }m}}
\left\{\alpha_m\,\ell_{t-1}(a_{mi},i)\right\},
\qquad
c_t(i)=c_{t-1}(i)+\delta c_t(i).
\]
</div>

If no eligible decoy covers a column, its increment is zero. This is a **signed contribution rule**: a negative column contribution can produce a negative increment. It should not be interpreted as a guarantee that every individual column score decreases.

For a single fixed alignment whose score is entirely the sum of its column contributions, the motivation for the weight is

<div markdown="0">
\[
S_m-\sum_i\alpha_m\ell_{t-1}(a_{mi},i)
=S_m-\alpha_m S_m=S_0.
\]
</div>

This exact identity assumes no separate gap-cost contribution. In a gapped search, gap costs and changes in the best alignment mean that the identity motivates the rule rather than guarantees the final reported score. All scores and the cutoff must use consistent units.

</details>

## How the correction fits into a profile

An amino-acid profile normally contains a normalized distribution at each column. The corrected log-odds score is

<div markdown="0">
\[
\ell_t(a,i)=\log_2\!\left(\frac{p_t(a,i)}{p_{\mathrm{bg}}(a)}\right)-c_t(i).
\]
</div>

Here pₜ(a, i) is the weighted amino-acid frequency estimated from the current MSA, and pbg(a) is its background frequency. Subtracting the same correction from every amino-acid score in a column changes how much that column contributes to a match, while preserving its relative amino-acid preferences.

The correction can be encoded by scaling the column's stored weights:

<div markdown="0">
\[
p'_t(a,i)=p_t(a,i)\,2^{-c_t(i)},
\qquad
\log_2\!\left(\frac{p'_t(a,i)}{p_{\mathrm{bg}}(a)}\right)
=\ell_t(a,i).
\]
</div>

**These corrected weights are not normalized probabilities.** Renormalizing them to sum to 1 would remove the correction. This representation lets the existing scoring machinery consume the adjustment without introducing a new profile field.

<details class="technical-note" markdown="1">
<summary>Recovering the correction in the next iteration</summary>

Because the uncorrected column probabilities sum to 1, the stored column sum records the accumulated correction:

<div markdown="0">
\[
\sum_a p'_t(a,i)=2^{-c_t(i)},
\qquad
c_t(i)=-\log_2\sum_a p'_t(a,i).
\]
</div>

The next iteration can recover this value, add its new decoy-based increment, and encode the result in the newly estimated profile. These expressions use bits. With natural-log scores, the equivalent scaling factor is exp(−c) and the recovery uses the natural logarithm.

</details>

## How we evaluate whether it helps

The corrections address two related but different questions:

- **Does the search rank real homologs more reliably?** Benchmark the k-mer prefilter and alignment stage separately, tune parameters on held-out validation data, and evaluate search sensitivity. The original gappiness benchmarks reported an increase in AUC; numerical effect sizes are not reproduced here.
- **Are the reported E-values better calibrated?** Test on a separately scrambled decoy database, rather than the decoys used to derive the correction. Compare observed false-positive counts with the counts implied by the reported E-values.

For a log–log calibration plot, counts should be put on the appropriate scale before comparing them with a diagonal. With Q query profiles and a decoy database the same size as the real target database, the ideal aggregate count below an E-value threshold E is approximately Q × E. Counts per query can therefore be compared with E; different database sizes require a corresponding adjustment.

The figures on this page are explanatory examples. They show the mechanism and its boundary cases, rather than substitute for an empirical benchmark.

## Codebase and further reading

- [MMseqs2 source code](https://github.com/soedinglab/MMseqs2)
- [MMseqs2 user guide](https://github.com/soedinglab/MMseqs2/wiki), including profile construction, prefiltering, and alignment.

{% include technical_note_math.html %}
