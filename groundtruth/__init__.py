"""Ground Truth: the deterministic parts of a multi-agent job search.

- ``groundtruth.screen`` - rule-based first pass over parsed job listings.
- ``groundtruth.check``  - mechanical claims check of a tailored résumé (and letter)
  against the master résumé and a retired-claims list.
- ``groundtruth.state``  - the dedupe ledger: what was already judged, so nothing is
  judged twice.

Standard library only. Models do the judgment; this code does the rules.
"""

__all__ = ["screen", "check", "state"]
