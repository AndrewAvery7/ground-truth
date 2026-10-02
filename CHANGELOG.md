# Changelog

## 1.1.1 — 2026-10-01

- Both films now end holding their title card instead of fading to black, so a player
  that stops on its last frame still shows "Ground Truth" rather than a black screen.
  Picture, narration, music and length are otherwise unchanged.

## 1.1.0 — 2026-10-01

- The film ships with the code: `media/ground-truth-film.mp4` (93 s, 720p, captions burned
  in), a 36-second square cut, the poster and a WebVTT captions file. The demo screens in
  it use the same fictional candidate as `examples/`; the funnel numbers are the live
  system's first three days.
- README opens with the film.

## 1.0.0 — 2026-10-01

First public release of the public half of Ground Truth, a live multi-agent job
search running twice daily since 29 September 2026.

- Agent instruction files for all eight specialist roles, plus the Submit Assistant
  and the run-report template — sanitized of all personal data.
- `groundtruth/screen.py` (the deterministic screener) and `groundtruth/check.py`
  (the claims checker), standard library only, with tests.
- Runnable examples using a fictional candidate and invented employers.
- The four non-negotiables (GUARDRAILS.md).
