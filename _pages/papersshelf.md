---
layout: papersshelf
permalink: /papersshelf/
title: Papers Shelf
description: A collection of some papers on various topics. Keeping an organized list helps in building mental models and quickly remembering the crux of the work.
nav: true
nav_order: 1
---
<div id="chart"></div>

<script>
const papers = [
  {
    "title": "Solving SPDE giving a Matérn random field using the FEM",
    "author": "H. Bakka",
    "year": 2018,
    "link": "https://arxiv.org/abs/1803.03765",
    "abstract": "",
    "math": 80,
    "statistics": 15,
    "comp_sci": 5,
    "finance": 0
  },
  {
    "title": "The Recovery Theorem",
    "author": "Ross, S.",
    "year": 2015,
    "link": "https://www.jstor.org/stable/30035052",
    "abstract": "Shows how to recover the natural probability measure R from market prices of derivative securities.",
    "math": 0,
    "statistics": 20,
    "comp_sci": 10,
    "finance": 70
  },
  {
    "title": "Variable Selection Methods in regression models for binary data",
    "author": "S. Bag",
    "year": 2017,
    "link": "https://arxiv.org/abs/1601.00670",
    "abstract": "In this paper, we explore four main typologies (test-based, penalty-based, screening-based, and tree-based) of frequentist variable selection methods in logistic regression setup.",
    "math": 0,
    "statistics": 95,
    "comp_sci": 5,
    "finance": 0
  },
  {
    "title": "Neural Additive Models",
    "author": "Agarwal, R., Frosst, N., Zhang, X., Caruana, R., and Hinton, G.",
    "year": 2020,
    "link": "https://arxiv.org/abs/2004.13912",
    "abstract": "Interpretable Machine Learning with Neural Nets",
    "math": 10,
    "statistics": 30,
    "comp_sci": 60,
    "finance": 0
  },
  {
    "title": "NAMLSS: Neural Additive Models for Location Scale and Shape",
    "author": "Thielmann, A., Kruse, R., Kneib, T., Safken, B.",
    "year": 2023,
    "link": "https://arxiv.org/abs/2301.11862",
    "abstract": "Distributional Regression using Machine Learning",
    "math": 10,
    "statistics": 30,
    "comp_sci": 60,
    "finance": 0
  },
  {
    "title": "How Interpretable and Trustworthy are GAMs?",
    "author": "Benjamin L, S Tan, C Chang, G Hooker and R Caruana",
    "year": 2020,
    "link": "https://arxiv.org/abs/2006.06466",
    "abstract": "Which GAM should we trust?",
    "math": 10,
    "statistics": 45,
    "comp_sci": 45,
    "finance": 0
  },
  {
    "title": "Purifying Interaction Effects with the Functional ANOVA",
    "author": "Benjamin L, S Tan, C Chang, G Hooker and R Caruana",
    "year": 2020,
    "link": "https://arxiv.org/abs/1911.04974",
    "abstract": "An Efficient Algorithm for Recovering Identifiable Additive Models",
    "math": 20,
    "statistics": 40,
    "comp_sci": 40,
    "finance": 0
  },
  {
    "title": "Sparse Sequence-to-Sequence Models",
    "author": "B. Peters, V. Niculae and A. Martins ",
    "year": 2019,
    "link": "https://arxiv.org/abs/1905.05702",
    "abstract": "Introduces alpha entmax",
    "math": 30,
    "statistics": 30,
    "comp_sci": 40,
    "finance": 0
  },
  {
    "title": "NODE: Neural Oblivious Decision Ensembles",
    "author": "Popov S., Stanislav S., Babenko A.",
    "year": 2019,
    "link": "https://arxiv.org/abs/1909.06312",
    "abstract": "Generalizes ensembles of oblivious decision trees, but benefits from both end-to-end gradient-based optimization",
    "math": 10,
    "statistics": 60,
    "comp_sci": 30,
    "finance": 0
  },
  {
    "title": "GAMLSS: Generalized Additive Models for Location Scale and Shape",
    "author": "Mikis D., Rigby R.",
    "year": 2007,
    "link": "https://www.jstatsoft.org/article/view/v023i07",
    "abstract": "Foundational work in Distributional Regression",
    "math": 10,
    "statistics": 70,
    "comp_sci": 20,
    "finance": 0
  },
  {
    "title": "NODE-GAM: Neural Generalized Additive Model for Interpretable Deep Learning",
    "author": "C Chang, R Caruana, A Goldenberg",
    "year": 2021,
    "link": "https://arxiv.org/abs/2106.01613",
    "abstract": "Combines Node and GAMs",
    "math": 10,
    "statistics": 70,
    "comp_sci": 20,
    "finance": 0
  },
  {
    "title": "Attention is All You Need",
    "author": "Vaswani, A.",
    "year": 2017,
    "link": "https://arxiv.org/abs/1706.03762",
    "abstract": "Proposed the Transformer architecture, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
    "math": 10,
    "statistics": 20,
    "comp_sci": 70,
    "finance": 0
  },
  {
    "title": "Tab-Transformer: Tabular Data Modeling Using Contextual Embeddings",
    "author": "Huang, X., Khetan, A., Cvitkovic, M., & Karnin, Z.",
    "year": 2020,
    "link": "https://arxiv.org/abs/2012.06678v1",
    "abstract": "Built upon self-attention based Transformers. ",
    "math": 10,
    "statistics": 20,
    "comp_sci": 70,
    "finance": 0
  }
];
</script>