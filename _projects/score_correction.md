---
layout: page
title: Score Correction
description: Improving the match scores of sequence matches.
img:
importance: 4
category: Major
---

## Gappiness Match Score Correction

We wanted to give lower match scores to profile columns in gappy, less conserved regions than to columns in well-conserved regions with few gaps. Gappy referred not to the fraction of gaps overall but to the density of gap openings and endings. For example, an N-terminal region of 50 residues with only one sequence in a MSA with 100 sequences was not considered gappy despite a 99% gap fraction because no gaps opened or ended within these 50 residues. The contribution of amino acid conservation was taken care of by the standard log-odds scores of sequence profiles: Less conserved columns had lower top scores than well-conserved columns. But the information of gap open and gap end density was not used. It would have been particularly valuable to use in the prefilter to generate more k-mers in ungapped and fewer in gappy regions.

We measured the gappiness of blocks of $$W = 2D+1$$ columns (e.g., 15) around residue $$i$$ in the MSA by the fraction of sequences containing nogap in the block out of all sequences with at least one residue in the block,

$$
f_i = \frac{\sum_{n} w_n I(x_n, i-D : i+D \text{ contains no gap})}{\sum_{n} w_n I(x_n, i-D : i+D \text{ contains at least one residue})}
$$

where $$I(.)$$ was the indicator function and $$w_n$$ were the sequence weights. We defined a penalty function 

$$
\delta_i = - \log_2 \left[ \frac{(\beta + f_i)}{(\beta + 1)} \right] .
$$

When every sequence that had a residue in the block contained a gap in the block ($$f_i=0$$), the penalty was strongest, $$- \log_2[\beta/(\beta+1)] > 0$$. When the block contained no gaps at all ($$f_i=1$$), the penalty $$\delta_i$$ was zero. The constant $$\beta$$ prevented the logarithm from becoming too negative for small $$f_i$$. For example, if $$\beta=1/3$$ and if 50% of the W-mers around column $$i$$ were gappy in the sense that they contained both a residue and a gap, $$\delta_i$$ would have been $$\log_2[(5/6)/(4/3)] = -0.68$$ bits, if 75% were gappy, the penalty would have been -1.19 bits and if 99.9% were gappy it would have been -1.996 bits.

We could directly use $$\delta_i$$ as a score correction. But imagine the previous MSA with 100 sequences, 99 of which only started at column 51. In this example, $$\delta_i$$ would have been zero for $$i \leq 50-D$$ and $$i \geq 51+D$$. Between those positions, $$\delta_i$$ would have dropped from 0 to almost -2 bits. That would mean to align a sequence across that region would have incurred a hefty penalty of $$-W \times 2$$ bits, even though the MSA was not gappy at all. We remedied this situation by using as score correction $$\Delta S_i$$ for column $$i$$ the maximum of $$\delta_j$$ over all blocks that contained column $$i$$,

$$
\Delta S_i = \max\{\delta_j : j = i-D, \ldots, i+D\} .
$$

This penalty would have been zero at all positions in the example MSA. It would, however, still have penalized disordered regions with gaps every, say, 10 residues or so, if we chose $$D = 15$$. A good guess for $$\beta$$ was between 0.3 and 2.

This penalty $$\Delta S_i$$ could simply have been added directly to each of the scores in the query sequence profile. Therefore, no change in the sequence profile format was necessary. The score correction would then automatically have been used both in the prefilter to compute the list of similar k-mers and for the Smith-Waterman alignment stage.

To compensate for the negative average shift of the scores, we had to add a slight offset to every score:

$$
\Delta S_i = \max\{\delta_j : j = i-D, \ldots, i+D\} + A + B \times N_{\text{eff}},
$$

where $$N_{\text{eff}}$$ was the effective number of sequences in the block. Benchmarking had to include optimization of $$\beta$$, $$D$$, $$A$$, and $$B$$ on a validation set independent of the test set. (The score offset $$A$$ was already implemented in MMseqs2.) Finally, we benchmarked the effect of the gappiness penalty on the k-mer prefiltering and the effect on the SW alignments separately and found a significant increase in the AUC.

## Score correction for sequence profiles

Motivation: It had been observed by many that profile searches generally generated many more high-scoring false positive matches than sequence-sequence searches. In other words: the E-values computed based on the Karlin-Altschul statistic developed for sequence-sequence searches seemed to be much less reliable for profile searches. In particular, while most sequence profiles behaved well, a small fraction of profiles (<5%) behaved badly and generated many high-scoring false positive matches. In a sequence-to-profile search this could completely destroy the sensitivity at the first false positive (AUC1). 

We proposed a scheme to suppress these high-scoring false positives by targeted reduction of the scores in the problematic regions of these profiles. This score reduction was just strong enough to avoid the high-scoring false positives while being weak enough to still allow the corrected regions to match homologous regions.

To avoid including non-homologous stretches of sequence during the iterative searches to build the profile, we also applied the score correction to the evolving query profile before each search iteration. 

Correction: In order to keep track of false positives during iterative profile searching, we added to the normal target database a database of reverted or scrambled sequences (xm). Suppose we had performed the t'th search iteration with our query profile, and we obtained match scores of the scrambled sequences $$S_m$$, for $$m \in \{1,..,M\}$$. We denoted with $$S_0$$ the score corresponding to an E-value of 1 (with respect to the normal target db). 

The sequence profile to be constructed from the MSA of matched sequences after the t'th search iteration had scores

$$
s(x_{mi}, i) = \log\left[\frac{p(i,a)}{p_{bg}(a)}\right] - s_t(i), 
$$

where $$p(i,a)$$ was the weighted fraction of amino acid a at

 position i in the MSA, $$p_{bg}(a)$$ was the background frequency of amino acid a taken from the substitution matrix that was used for the pseudocounts, and $$s_t(i)$$ was the score correction. This correction was the sum of the score correction from the previous iteration, $$s_{t-1}(i)$$, and the contribution from the current iteration, $$\delta s_t(i)$$,

$$
s_t(i) = s_{t-1}(i) + \delta s_t(i).
$$

The contribution from the current iteration was 

$$
\delta s_t(i) = \max_m \left\{ \frac{(S_m - S_0)}{S_m} \times s(x_{mj}, i) : S_m > S_0, x_{mj} \text{ is residue in } x_m \text{ aligned to column } i\right\}.
$$

The condition $$S_m > S_0$$ was equivalent to $$E < 1$$, so only FP sequences with E-values < 1 could contribute to the score correction. The more the score of the FP match surpassed $$S_0$$, the more its weight $$(S_m - S_0)/S_m$$ tended to 1. The score correction $$\delta s(i)$$ was now simply the maximum of the weighted scores of profile column i with the high-scoring FP matches. The functional form of the weight could be motivated by assuming a single high-scoring FP sequence with score $$S_m$$. After the score correction, its score would have been 

$$
S_m - \sum_i \delta t_s(i) = S_m - \frac{(S_m - S_0)}{S_m} \times S_m = S_0,
$$

so the E-value of this sequence would have been $$E=1$$ after the correction.

This correction scheme could of course also have been applied to profiles post hoc, by searching only the database of scrambled sequences (but setting $$S_0$$ such that it corresponded to E=1 in the target db), in which case the correction was simply $$s_t(i) = \delta s_t(i)$$.

Implementation: The implementation in mmseqs2 was easy and did not require any change in the mmseqs profile format! We noted that the corrected scores were obtained by multiplying each probability by $$\exp[-s_t(i)]$$:

$$
s(x_{mi},i) = \log \left[ \frac{p_t(a,i)}{p_{bg}(a)} \right]  
s(x_{mi},i) - s_t(i) = \log \left[ \frac{p_t(a,i) \exp[-s_t(i)]}{p_{bg}(a)} \right] 
s(x_{mi},i) - s_t(i) = \log \left[ \frac{p'_t(a,i)}{p_{bg}(a)} \right], \text{ with } 
p'_t(a,i) = p_t(a,i) \exp[-s_t(i)] 
$$

Therefore, the score correction could be entirely encoded in the probabilities. We extracted the score correction included in the query profile used for the t'th iteration using

$$
s_{t-1}(i) = - \log \sum_a p_{t-1}(i,a).
$$

We then added the contribution from the last search iteration, $$\delta s_t(i)$$, to this correction to obtain the correction $$s_t(i)$$ for the new query profile. This correction was encoded in the new query profile using $$p'_t(i,a) = p_t(a,i) \exp(- s_t(i))$$.

Tests: We tested the effectiveness of the score correction by searching with a set of uncorrected and corrected sequence profiles through a database of reverted or scrambled sequences (using a different scrambling than the one used to derive the score correction) and plotting the number of FP matches with an E-value better than the one on the x-axis. On a log-log plot, the numbers ideally were close to the diagonal line after the correction, whereas before the correction, strong deviations for small E-values could be expected for some profiles.

Profile-profile comparison: We simply used the same correction of the profile probabilities.

Codebase: [https://github.com/soedinglab/MMseqs2](https://github.com/soedinglab/MMseqs2)