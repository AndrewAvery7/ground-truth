# The agents

These are the live system's instruction files — one per role — with every personal
detail removed. They are written for a model to follow, in plain English, and they are
the operational design of the system: what each role may and may not do, what it hands
on, and what it must report.

Two of the components they call ship here as code: the Screener
([`groundtruth/screen.py`](../groundtruth/screen.py)) and the Checker's mechanical pass
([`groundtruth/check.py`](../groundtruth/check.py)). Other paths and modules the files
mention (`pipeline.*`, `state/...`, the tracker queue, the document builder) describe the
private implementation and are not included: they are tied to the owner's own tracker,
inbox and documents.

| File | Role |
|---|---|
| [scout.md](scout.md) | Reads and files the alert emails; hands listings to the Screener |
| [researcher.md](researcher.md) | Finds the employer's real posting; catches closed, renamed and inflated listings |
| [fit-judge.md](fit-judge.md) | Apply, Stretch or Skip, and the hand-off to the tracker |
| [tailor.md](tailor.md) | Drafts the package from the untouched master |
| [checker.md](checker.md) | Independent review: every claim against the master — PASS or HOLD |
| [clerk.md](clerk.md) | Reads employer replies; never sends, replies or deletes |
| [coach.md](coach.md) | The weekly review: one pattern, one suggestion, no decisions |
| [submit.md](submit.md) | Live sessions only: fills a form, submits only on a role-named yes |
| [report-template.md](report-template.md) | The shape of every run's report |
