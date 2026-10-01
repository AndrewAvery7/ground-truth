"""Mechanical checks on a tailored package. The Checker agent runs this FIRST, then reads
the documents itself for anything a rule can't see (a claim stretched in wording, a tone
problem). A package that fails here is held, whatever the agent thinks.

    python -m groundtruth.check <resume.md> --master master-resume.md
                                [--retired retired-claims.txt]
                                [--letter letter.md] [--company "Acme"]

Input is plain text or Markdown (UTF-8), read with the standard library only. One line is
one paragraph. Markdown heading markers (``#``) are ignored; lines starting with ``-``, ``*``
or ``•`` are bullets. A section heading is a short line in CAPITALS ("PROFESSIONAL
EXPERIENCE"). Emphasis markers (``**``) count as leftover markup, so keep the files plain.

Checks:
  * every figure ($, %, and numbers of 2+ digits) in the résumé and letter appears in the
    master; each failure cites the line it came from
  * no retired or withdrawn claim appears (the --retired list: one phrase per line,
    ``#`` comments allowed; matched case-insensitively)
  * employer, title and date lines, education and certifications are word-for-word the master's
  * the name and contact lines (everything above the master's first section heading) are
    unchanged and near the top
  * the letter names the company, runs 200-420 words, and has no placeholders
Prints JSON {"pass": bool, "verdict": "PASS"|"HOLD", "errors": [...], "warnings": [...]};
exit 1 on any error.

Page counts are NOT checked here (plain-text input has no pages): render the final
documents and check their length separately.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

FIGURE = re.compile(r"\$[\d.,]+\s*[KMB]?\+?|\b\d+(?:\.\d+)?\s?%|\b\d[\d,]*\d\+?\b")
DATE_LINE = re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? \d{4}\b|\t\s*\d{4}\s*$")
PLACEHOLDER = re.compile(r"\[(company|role|name|title|x+)\]|\bTODO\b|\bXX+\b|\{\{|\}\}|\*\*", re.I)
AI_TELLS = ["i am excited to apply", "i hope this finds you well", "delve", "tapestry", "testament to",
            "passionate about", "synerg", "leverage my", "in today's fast-paced", "i am confident that i",
            "dynamic environment", "unique blend"]
HEADING_MARK = re.compile(r"^\s{0,3}#{1,6}\s+")
BULLET_MARK = re.compile(r"^(\s*)[-*]\s+")


def paras(path):
    """The file's lines, as paragraphs: heading markers dropped, list markers turned into
    the bullet character the rules below look for."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [BULLET_MARK.sub(r"\1• ", HEADING_MARK.sub("", line)) for line in lines]


def norm(s):
    return re.sub(r"\s+", " ", s.replace(" ", " ")).strip()


def is_heading(s):
    return bool(s) and s.isupper() and len(s) < 40


def retired_phrases(path=None):
    if not path or not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        out = [l.strip() for l in f if l.strip() and not l.lstrip().startswith("#")]
    return sorted(set(out))


def figures(text):
    got = set()
    for m in FIGURE.finditer(text):
        f = re.sub(r"\s+", "", m.group(0))
        if re.fullmatch(r"(19|20)\d\d", f):
            continue                      # years are checked through the protected lines
        got.add(f)
    return got


def contact_lines(master):
    """Name and contact block: the non-empty lines above the first section heading."""
    out = []
    for t in master:
        s = norm(t)
        if is_heading(s):
            break
        if s:
            out.append(s)
    return out


def protected_lines(master):
    """Lines a tailoring may never change: employer, title and date lines (non-bullet lines in
    the experience section, and any tab-separated line ending in a date), plus education and
    certifications. Bullets and the summary are fair game for rewording; the Checker agent
    judges those by meaning."""
    out, section = [], ""
    for t in master:
        s = norm(t)
        if not s:
            continue
        if is_heading(s):
            section = s
            continue
        bullet = t.lstrip().startswith("•")
        if section == "PROFESSIONAL EXPERIENCE" and not bullet:
            out.append(s)
        elif not bullet and "\t" in t and DATE_LINE.search(t):
            out.append(s)
        elif section in ("EDUCATION", "CERTIFICATIONS"):
            out.append(s)
    return out


def _cite(lines, pred):
    """The first non-empty line satisfying pred, shortened, for an error message."""
    for x in lines:
        s = norm(x)
        if s and pred(s):
            s = s.lstrip("• ").strip()
            return s if len(s) <= 120 else s[:117] + "..."
    return None


def _with_line(msg, line):
    return f"{msg} - line: {line!r}" if line else msg


def check(resume, letter=None, company=None, master=None, retired=None):
    errors, warnings = [], []
    if not master:
        raise ValueError("a master résumé path is required")
    m = paras(master)
    mtext = norm("\n".join(m))
    r = paras(resume)
    rtext = norm("\n".join(r))

    # 1. contact block
    top = [norm(x) for x in r if norm(x)][:8]
    for line in contact_lines(m):
        if line not in top:
            errors.append(f"contact line changed or missing: {line!r}")

    # 2. protected lines
    rset = {norm(x) for x in r}
    for line in protected_lines(m):
        if line not in rset:
            errors.append(f"protected line altered or removed: {line[:90]!r}")

    # 3. figures
    mfig = figures(mtext)
    for f in sorted(figures(rtext) - mfig):
        errors.append(_with_line(f"résumé figure not in the master: {f}",
                                 _cite(r, lambda s, f=f: f in figures(s))))

    # 4. retired claims
    forb = retired_phrases(retired)
    if retired is None:
        warnings.append("no retired-claims list given (--retired); retired claims not checked")
    elif not os.path.exists(retired):
        warnings.append(f"retired-claims list not found: {retired}")
    for ph in forb:
        if ph.lower() in rtext.lower():
            errors.append(_with_line(f"résumé contains a retired claim: {ph!r}",
                                     _cite(r, lambda s, ph=ph: ph.lower() in s.lower())))
    if PLACEHOLDER.search(rtext):
        errors.append(_with_line("résumé contains a placeholder or leftover markup",
                                 _cite(r, lambda s: bool(PLACEHOLDER.search(s)))))

    # 5. letter
    if letter:
        L = paras(letter)
        body = [norm(x) for x in L if norm(x)]
        ltext = "\n".join(body)
        # Same layout assumption as the original: a 7-line header (name, contact, date,
        # recipient) and a one-line sign-off around the body.
        body_only = [x for x in body[7:-1]] if len(body) > 8 else body
        words = len(" ".join(body_only).split())
        if not 200 <= words <= 420:
            errors.append(f"letter body is {words} words (want 200-420)")
        if company and company.lower() not in ltext.lower():
            errors.append(f"letter never names the company {company!r}")
        lfig = figures("\n".join(body_only))
        for f in sorted(lfig - mfig):
            errors.append(_with_line(f"letter figure not in the master: {f}",
                                     _cite(body_only, lambda s, f=f: f in figures(s))))
        for ph in forb:
            if ph.lower() in ltext.lower():
                errors.append(f"letter contains a retired claim: {ph!r}")
        if PLACEHOLDER.search(ltext):
            errors.append("letter contains a placeholder or leftover markup")
        for tell in AI_TELLS:
            if tell in ltext.lower():
                warnings.append(f"letter uses a stock phrase recruiters flag: {tell!r}")

    # 6. pages
    warnings.append("page count not checked (plain-text input; check the rendered documents)")

    return {"pass": not errors, "verdict": "PASS" if not errors else "HOLD",
            "errors": errors, "warnings": warnings, "retired_list_size": len(forb)}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Mechanical claims check of a tailored résumé.")
    ap.add_argument("resume", help="tailored résumé, .md or .txt")
    ap.add_argument("--master", required=True, help="master résumé, .md or .txt")
    ap.add_argument("--retired", help="retired-claims list, one phrase per line")
    ap.add_argument("--letter", help="cover letter, .md or .txt")
    ap.add_argument("--company")
    a = ap.parse_args(argv)
    out = check(a.resume, a.letter, a.company, a.master, a.retired)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
