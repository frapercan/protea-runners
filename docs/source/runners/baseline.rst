Baseline (``baseline``)
========================

A null / random runner used as the floor in ablation studies. Given
a query set and an annotation set, the baseline samples GO terms
from the empirical frequency distribution of the references without
using the embeddings at all. Anything that does not beat the
baseline is suspect.

:Status: contract-surface stub.
:Real path: pending; the baseline does not yet have an active
            implementation in ``protea-core``. It will be added
            either as a runner here, or as a fixed seed inside the
            evaluation pipeline.

Operational notes
-----------------

- The baseline is deliberately un-tuned. Its predictions reflect the
  prior on GO terms in the reference set, nothing more.
- A second baseline variant ("BLAST + IDF transfer") is a candidate
  for inclusion to compare against alignment-based methods on the
  same evaluation harness.

API reference
-------------

.. automodule:: protea_runners.baseline
   :members:
   :show-inheritance:
   :member-order: bysource
