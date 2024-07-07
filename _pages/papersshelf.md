---
layout: papersshelf
permalink: /papersshelf/
title: Papers Shelf
description: A collection of papers I've read on various topics. Keeping an organized list of the papers helps in building mental models and quickly remembering the crux of the work.
nav: true
nav_order: 1
---
<div id="chart"></div>

<script>
const papers = [
  {
    "title": "Solving SPDE giving a Matérn random field using the FEM",
    "author": "Haakon Bakka",
    "year": 2018,
    "link": "https://arxiv.org/abs/1803.03765",
    "abstract": "Abstract of the paper",
    "math": 80,
    "statistics": 15,
    "comp_sci": 5,
    "finance": 0
  },
  {
    "title": "Statistical Learning with Sparsity: The Lasso and Generalizations",
    "author": "Hastie, Tibshirani, Wainwright",
    "year": 2015,
    "link": "https://www.ime.unicamp.br/~dias/SLS.pdf",
    "abstract": "Abstract of the paper",
    "math": 10,
    "statistics": 80,
    "comp_sci": 10,
    "finance": 0
  },
  {
    "title": "BERT",
    "author": "Devlin, Chang, Lee, Toutanova",
    "year": 2019,
    "link": "https://dl.acm.org/doi/10.1145/3292500.3330701",
    "abstract": "Abstract of the paper",
    "math": 0,
    "statistics": 20,
    "comp_sci": 80,
    "finance": 0
  },
  {
    "title": "Portfolio Selection",
    "author": "Harry Markowitz",
    "year": 1952,
    "link": "https://www.math.ust.hk/~maykwok/courses/ma362/07F/markowitz_JF.pdf",
    "abstract": "Abstract of the paper",
    "math": 0,
    "statistics": 0,
    "comp_sci": 10,
    "finance": 90
  },
  {
    "title": "The Recovery Theorem",
    "author": "Ross, S.",
    "year": 2015,
    "link": "https://www.jstor.org/stable/30035052",
    "abstract": "Abstract of the paper",
    "math": 0,
    "statistics": 20,
    "comp_sci": 10,
    "finance": 70
  },
  {
    "title": "Bayesian Data Analysis",
    "author": "Andrew Gelman, John B. Carlin, Hal S. Stern, David B. Dunson, Aki Vehtari, Donald B. Rubin",
    "year": 2013,
    "link": "http://www.stat.columbia.edu/~gelman/book/",
    "abstract": "Abstract of the paper",
    "math": 20,
    "statistics": 60,
    "comp_sci": 20,
    "finance": 0
  },
  {
    "title": "Variational Inference I",
    "author": "Course Notes",
    "year": 2011,
    "link": "https://www.cs.princeton.edu/courses/archive/fall11/cos597C/lectures/variational-inference-i.pdf",
    "abstract": "Abstract of the paper",
    "math": 30,
    "statistics": 50,
    "comp_sci": 20,
    "finance": 0
  },
  {
    "title": "A Stochastic Approximation Method",
    "author": "Robbins, H. and Monro, S.",
    "year": 1951,
    "link": "https://www.columbia.edu/~ww2040/8100F16/RM51.pdf",
    "abstract": "Abstract of the paper",
    "math": 40,
    "statistics": 40,
    "comp_sci": 20,
    "finance": 0
  },
  {
    "title": "Variational Inference: A Review for Statisticians",
    "author": "Blei, D. M., Kucukelbir, A., McAuliffe, J. D.",
    "year": 2017,
    "link": "https://arxiv.org/pdf/1601.00670",
    "abstract": "Abstract of the paper",
    "math": 30,
    "statistics": 50,
    "comp_sci": 20,
    "finance": 0
  },
  {
    "title": "Neural Additive Models: Interpretable Machine Learning with Neural Nets",
    "author": "Agarwal, R., Frosst, N., Zhang, X., Caruana, R., and Hinton, G.",
    "year": 2020,
    "link": "https://arxiv.org/abs/2004.13912",
    "abstract": "Abstract of the paper",
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
    "abstract": "Abstract of the paper",
    "math": 10,
    "statistics": 30,
    "comp_sci": 60,
    "finance": 0
  },
  {
    "title": "Attention is All You Need",
    "author": "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I.",
    "year": 2017,
    "link": "https://arxiv.org/abs/1706.03762",
    "abstract": "Abstract of the paper",
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
    "abstract": "Abstract of the paper",
    "math": 10,
    "statistics": 20,
    "comp_sci": 70,
    "finance": 0
  },
  {
    "title": "A Non-Random Walk Down Wall Street",
    "author": "Andrew W. Lo, A. Craig MacKinlay",
    "year": 1999,
    "link": "https://press.princeton.edu/books/hardcover/9780691092563/a-non-random-walk-down-wall-street",
    "abstract": "Abstract of the paper",
    "math": 10,
    "statistics": 20,
    "comp_sci": 10,
    "finance": 60
  },
  {
    "title": "An Inquiry into the Nature and Causes of the Wealth of Nations",
    "author": "Adam Smith",
    "year": 1776,
    "link": "https://www.gutenberg.org/ebooks/3300",
    "abstract": "Abstract of the paper",
    "math": 0,
    "statistics": 20,
    "comp_sci": 0,
    "finance": 80
  },
  {
    "title": "Capital in the Twenty-First Century",
    "author": "Thomas Piketty",
    "year": 2013,
    "link": "https://www.hup.harvard.edu/catalog.php?isbn=9780674430006",
    "abstract": "Abstract of the paper",
    "math": 0,
    "statistics": 20,
    "comp_sci": 0,
    "finance": 80
  }
];
</script>