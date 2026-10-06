# Security policy

## Reporting a vulnerability

Please report security issues privately through
[GitHub's private vulnerability reporting](https://github.com/AndrewAvery7/ground-truth/security/advisories/new)
rather than opening a public issue. I aim to acknowledge reports within a few days.

## What matters most here

This project processes untrusted text (job-alert emails and employer postings).
The most useful reports are ways that text could be made to act as an instruction,
cause an application to be submitted, or get an unsupported claim past the claims
checker. See [GUARDRAILS.md](GUARDRAILS.md) for the rules the system is built around.

## Supported versions

Only the latest commit on `main` is supported.
