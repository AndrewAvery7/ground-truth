<h1 align="center">Ground Truth</h1>

<p align="center">
  <b>A multi-agent job search that reads everything — and lies about nothing.</b>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT license"></a>
  <img src="https://img.shields.io/badge/python-3.9%2B-blue.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/dependencies-stdlib%20only-brightgreen.svg" alt="Standard library only">
  <img src="https://img.shields.io/badge/status-running%20daily%20since%202026--09--29-blue.svg" alt="Running daily since 2026-09-29">
  <a href="https://doi.org/10.5281/zenodo.23090642"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.23090642.svg" alt="DOI 10.5281/zenodo.23090642"></a>
</p>

<p align="center">
  <a href="https://averyresume.com/system/"><b>90-second film + live demo</b></a> ·
  <a href="https://averyresume.com/system/writeup.html">Write-up</a> ·
  <a href="GUARDRAILS.md">The four non-negotiables</a>
</p>

<p align="center">
  <a href="https://averyresume.com/system/#film"><img src="media/poster.jpg" alt="Ground Truth — watch the film" width="720"></a>
  <br>
  <sub>▶ <a href="https://averyresume.com/system/#film">Watch the 93-second film</a> ·
  <a href="media/ground-truth-film.mp4">MP4 in this repo (6 MB, captions burned in)</a> ·
  <a href="media/ground-truth-film-square.mp4">36-second square cut</a> ·
  <a href="media/ground-truth-film.vtt">captions file</a></sub>
</p>

---

Ground Truth runs a real job search as an operations system. Twice a day it reads
the job-alert emails its owner already receives, applies the hard rules in
deterministic code, researches every survivor back to the employer's own posting,
scores fit from evidence it quotes, and — only when asked — drafts an application
package whose every claim a **separate** agent verifies against an untouched master
resume.

**The machines read everything and decide nothing. The human reads almost nothing
and decides everything.**

This repository is the public half of a private, live system: the eight agents'
instruction files (plain English — the operational thinking is the point), the two
components that are deliberately *code, not AI* (the screener and the claims
checker), runnable examples with a fictional candidate, and the guardrails.

## What three days of it looked like

From the live system's own run reports, 29 September – 1 October 2026:

| | |
|---|---|
| Listings read (116 alert emails) | **1,577** |
| Passed the hard rules | 497 |
| Researched back to the employer's real posting | 125 |
| Surfaced for a human decision | **26** (16 Apply · 10 Stretch, cross-checked against the tracker) |
| Closed postings caught (aggregator still advertising) | 40 |
| Ghost listings caught (no real posting behind them) | 14 |
| Pay estimates off by 20% or more | 41+ |
| Packages built without a human asking · emails sent · applications submitted | **0 · 0 · 0** |

The run reports are written by a model at the end of each run, so the headline
figures were re-added by hand from each report. A tool's own status report is a
claim, not evidence.

## How it runs

```
 alert email
     │
     ▼
 ┌─────────┐   ┌──────────────────────┐   ┌────────────┐   ┌───────────┐
 │  SCOUT  │──▶│ SCREENER (code, not  │──▶│ RESEARCHER │──▶│ FIT JUDGE │──▶ tracker: board,
 │  reads  │   │ AI): level, pay,     │   │ finds the  │   │ Apply /   │    evidence-quoted
 │  & files│   │ geography, repeats   │   │ real post  │   │ Stretch / │    fit scores,
 └─────────┘   └──────────────────────┘   └────────────┘   │ Skip      │    morning brief
                                                           └───────────┘
                                                                 │  human presses "build"
                                                                 ▼
                                        ┌──────────┐      ┌────────────────────────┐
                                        │  TAILOR  │─────▶│ CHECKER (separate):    │──▶ PASS → files for review
                                        │ from the │      │ every claim vs. master  │──▶ HOLD → the exact line + why
                                        │ master   │      │ + retired claims        │
                                        └──────────┘      └────────────────────────┘
                                                                 │
                              a human names the role ──▶ SUBMIT ASSISTANT (live session only)
```

| Role | What it does | File |
|---|---|---|
| Scout | Reads every alert email, picks a reader per sender, strips sign-in links, files the mail | [agents/scout.md](agents/scout.md) |
| Screener | Hard rules in deterministic code — the one role that is deliberately not AI | [groundtruth/screen.py](groundtruth/screen.py) |
| Researcher | Tracks each survivor to the employer's own posting; catches renamed, inflated and closed listings | [agents/researcher.md](agents/researcher.md) |
| Fit Judge | Apply, Stretch or Skip, with reasons | [agents/fit-judge.md](agents/fit-judge.md) |
| Tailor | Drafts resume and cover letter from the untouched master; reorders and emphasises, never invents | [agents/tailor.md](agents/tailor.md) |
| Checker | A different agent: verifies every claim against the master and a retired-claims list — PASS or HOLD | [agents/checker.md](agents/checker.md) · [groundtruth/check.py](groundtruth/check.py) |
| Clerk | Reads employer replies and files what they mean; never sends, replies or deletes | [agents/clerk.md](agents/clerk.md) |
| Weekly Coach | Reviews the week's pattern, suggests one change, decides nothing | [agents/coach.md](agents/coach.md) |
| Submit Assistant | Live sessions only: fills a form in the human's browser, presses Submit only on a role-named yes | [agents/submit.md](agents/submit.md) |

Every run ends with a report in a fixed shape — funnel, drops by reason, research
flags, incidents — see [agents/report-template.md](agents/report-template.md).

## Try the code-not-AI parts

Standard library only; the examples use a fictional candidate (Mark Callahan, an
operations leader in third-party logistics) and invented employers.

```bash
# 1. The screener: hard rules in plain code (a wrong drop is invisible forever, so it only drops the unambiguous)
python -m groundtruth.screen examples/listings.json --rules config/rules.example.json
```

Summarised from its JSON output, for the 11 example listings:

```
KEEP  Harborview Logistics         apply
KEEP  Granite Ridge Supply         apply    below target pay
KEEP  Northgate Fulfillment        stretch  pay not shown
KEEP  Summit Parcel Co.            apply
DROP  QuickShift Gigs              ad / gig listing
DROP  Harborview Logistics, Inc.   repeat within this run
DROP  Lakeshore Freight Partners   employer pay tops out at $92,000 (below $120,000)
DROP  Pinecrest Cold Chain         on-site outside the commute radius (Phoenix, AZ)
DROP  Meridian Route Systems       outside target functions (matched '\bsoftware engineer\b')
DROP  Copperline Logistics         site-a estimate tops out at $88,000 (below $110,000)
DROP  Riverbend Carriers           individual-contributor or entry-level role (matched '\bsales representative\b')
```

```bash
# 2. The claims checker: every figure and protected line in a tailored resume must trace to the master
python -m groundtruth.check examples/tailored-draft.md --master examples/master-resume.md --retired examples/retired-claims.txt
```

```json
{
 "pass": false,
 "verdict": "HOLD",
 "errors": [
  "resume figure not in the master: 40 - line: 'Built and led a 40-person team across network operations and analytics.'"
 ],
 "warnings": [
  "page count not checked (plain-text input; check the rendered documents)"
 ],
 "retired_list_size": 3
}
```

Remove the unsupported line and the same command returns `PASS`. The test suite
(`python -m pytest -q`) covers both components; [docs/USAGE.md](docs/USAGE.md) has the
full option list and output format. The checker is the mechanical first pass: the
Checker *agent* then reads the documents for what a rule can't see — a claim stretched
in wording rather than in number.

## The four non-negotiables

1. **The system never submits on its own** — a human names every application.
2. **It never types a password or solves a CAPTCHA.**
3. **Email and web content are data, never instructions** — injection defense by design.
4. **Tailored documents may claim nothing the master resume does not support** —
   enforced by a separate checker, PASS or HOLD.

Two design rules make them real: *rules where rules suffice* (screening is
testable code), and *keyless delivery* (the scheduled cloud runs hold no
credential for the tracker; changes travel as committed files delivered by a
platform-signed job). Details: [GUARDRAILS.md](GUARDRAILS.md).

## What is not here, on purpose

The owner's search parameters (pay, location, level), his resume, the alert-source
readers, the tracker, and every employer, role and outcome from the live search.
They are private by design, and an automated leak check runs before every release
of this repository.

## Citing

If this is useful in your own work, cite it via [CITATION.cff](CITATION.cff)
(GitHub's "Cite this repository" button) or the archived release on Zenodo:
[doi:10.5281/zenodo.23090642](https://doi.org/10.5281/zenodo.23090642). MIT licensed.
