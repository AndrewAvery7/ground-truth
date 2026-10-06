# Contributing

Issues and PRs are welcome. This repository is the public half of a private, live
system, so changes here should keep the examples, agent instructions and
guardrails honest rather than add features.

The most valuable contributions:

- **Screener rules and edge cases.** Listings that the deterministic screener
  (`python -m groundtruth.screen`) classifies wrongly, with the listing text
  (sanitised) and the rules file you used.
- **Claims-checker gaps.** A tailored line that the checker
  (`python -m groundtruth.check`) lets through but the master resume does not
  support. This is the highest-value report: it is the project's central promise.
- **Prompt-injection cases.** Email or posting text that gets an agent to treat
  data as instructions. See [GUARDRAILS.md](GUARDRAILS.md).

House rules:

- **Standard library only.** No new runtime dependencies.
- **The four non-negotiables in [GUARDRAILS.md](GUARDRAILS.md) are not
  negotiable:** nothing submits on its own, nothing types a password or solves a
  CAPTCHA, email and web content stay data, and tailored text claims nothing the
  master resume does not support.
- **The screener and checker stay code, not AI.**
- **Examples use the fictional candidate only.** No real names, employers,
  addresses or listings.
- Run `python -m pytest -q` before opening a PR, and say what you ran.
