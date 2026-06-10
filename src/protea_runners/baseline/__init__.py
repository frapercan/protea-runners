"""Reference baselines for reproducibility.

Implements :class:`protea_contracts.ExperimentRunner` (via
:class:`protea_runners._base.StubRunner`) as a thin shell that runs
CAFA-style reference baselines (e.g. naive frequency, BLAST-based
predictions) against a frozen dataset. The plugin is the contract
surface; no active baseline implementation lives in PROTEA or the lab
today, so the three lifecycle methods are stubs that fail loud rather
than no-op'ing.

Why this plugin exists pre-implementation: the master plan v3 narrative
calls for ablation tables that compare PROTEA's reranker against the
same naive / BLAST baselines that CAFA evaluates. Having the
entry_point reserved means the experiment dispatch layer can treat
``runner == "baseline"`` as a known unknown rather than an unrecognised
name.
"""

from __future__ import annotations

from typing import ClassVar

from protea_runners._base import StubRunner


class BaselineRunner(StubRunner):
    """Reference baseline runner (naive frequency, BLAST, ...).

    Stub during F2A.8: no active baseline implementation exists yet. The
    plan is to land naive-frequency and BLAST-based baselines as part of
    the F-EXP narrative work in master plan v3.
    """

    name = "baseline"

    stub_pointers: ClassVar[dict[str, str]] = {
        "fit": (
            "No active baseline implementation exists yet; this entry_point "
            "is reserved for the F-EXP narrative work in master plan v3."
        ),
        "evaluate": (
            "No active baseline implementation exists yet; this is reserved "
            "for the F-EXP narrative work in master plan v3."
        ),
        "export": "No active baseline implementation exists yet.",
    }


#: Module-level plugin instance discovered via the
#: ``protea.runners`` entry_points group.
plugin = BaselineRunner()
