"""Rule-based first pass over parsed listings: drop the clear misses, mark the rest.

This is deliberately conservative. It removes only what is unambiguous: ads and gig work,
repeats, roles already in the tracker or already judged, pay the EMPLOYER states is below
the pay floor (or a listing site's estimate below a lower skip line), on-site roles outside
a commute radius around home, and clearly-wrong functions. Everything uncertain goes
forward to the Fit Judge, which is a model reading the real posting. A wrong drop here is
invisible forever; a wrong keep costs one lookup.

The rules live in a JSON file (see ``config/rules.example.json``):

* a pay floor, a flagged band and a skip line - employer pay below the floor is dropped,
  pay between the floor and the target is kept but flagged, and a listing site's *estimate*
  is dropped only below its own (lower) skip line, because estimates are often wrong;
* a commute radius around home - expressed as the list of towns inside it; remote roles
  pass when remote is allowed, and an unknown location ("3 Locations") always passes;
* a target level and a stretch level - title patterns that mark a kept role "apply" or
  "stretch" (or "unclear" when neither matches); this is a label, never a drop.

    python -m groundtruth.screen listings.json [--rules config/rules.example.json]
        [--snapshot tracker_snapshot.json] [--today 2026-10-01]
        [--state state/seen.json] [--write-state]

prints {"candidates": [...], "dropped": [...], "counts": {...}}.

A listing is a dict with at least ``company`` and ``title``; optional fields are
``pay_min``, ``pay_max``, ``pay_estimated``, ``remote``, ``location``, ``posted``,
``source`` and ``key``. A tracker snapshot is {"roles": [{"company", "role", "stage"}]}.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys

from . import state as ledger

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_RULES = os.path.join(ROOT, "config", "rules.example.json")

# Legal-form words that vary between alert sources for the same employer ("Acme, Inc." vs "Acme").
SUFFIXES = re.compile(r"\b(inc|llc|l\.l\.c|ltd|corp|corporation|co|company|plc|lp|llp|pbc|group|holdings)\b\.?", re.I)


def make_key(company: str, title: str) -> str:
    """Stable dedupe key "<company>|<title>": lowercase, legal suffixes and punctuation
    removed, and remote/hybrid markers stripped from the title, so the same role sent by
    two alert sources (or twice by one) collapses to one key."""
    c = SUFFIXES.sub(" ", company.lower())
    c = re.sub(r"[^a-z0-9]+", " ", c).strip()
    t = title.lower()
    t = re.sub(r"\((remote|hybrid)[^)]*\)|\bremote\b|-\s*remote\b", " ", t)
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    return f"{c}|{t}"


def load_rules(path=None):
    with open(path or DEFAULT_RULES, encoding="utf-8") as f:
        return json.load(f)


def level_of(title: str, rules) -> str:
    """Label a title with the target level ("apply"), the stretch level ("stretch"), or
    "unclear". Override patterns are checked first, for titles that contain a stretch-level
    phrase but sit at the target level (an "Associate Vice President" contains "Vice
    President")."""
    t = title.lower()
    if any(re.search(p, t) for p in rules.get("apply_override_patterns", [])):
        return "apply"
    if any(re.search(p, t) for p in rules["stretch_title_patterns"]):
        return "stretch"
    if any(re.search(p, t) for p in rules["apply_title_patterns"]):
        return "apply"
    return "unclear"


def location_ok(rec, rules) -> bool:
    """Inside the commute radius, remote (when allowed), or unknown."""
    if rec.get("remote") and rules["location"]["allow_remote"]:
        return True
    loc = (rec.get("location") or "").lower()
    if not loc or re.fullmatch(r"\d+\s+locations?|multiple locations|various locations|see (the )?posting", loc.strip()):
        return True          # unknown ("3 Locations"): let the Researcher find out
    return any(c in loc for c in rules["location"]["local_cities"])


def pay_verdict(rec, rules):
    """Returns (drop_reason or None, note or '')."""
    hi = rec.get("pay_max")
    if not hi:
        return None, "pay not shown"
    p = rules["pay"]
    if rec.get("pay_estimated"):
        if hi < p["estimate_floor"]:
            return f"{rec.get('source') or 'listing-site'} estimate tops out at ${hi:,} (below ${p['estimate_floor']:,})", ""
        return None, f"pay is {rec.get('source') or 'the listing site'}'s estimate"
    if hi < p["floor"]:
        return f"employer pay tops out at ${hi:,} (below ${p['floor']:,})", ""
    if hi < p["target"]:
        return None, "below target pay"
    return None, ""


def screen(listings, rules, snapshot=None, state=None, today=None):
    today = today or dt.date.today().isoformat()
    state = state if state is not None else {}
    tracker_keys = {}
    for r in (snapshot or {}).get("roles", []):
        tracker_keys[make_key(r.get("company", ""), r.get("role", ""))] = r
    cutoff = (dt.date.fromisoformat(today) - dt.timedelta(days=rules["dedupe_days"])).isoformat()

    seen_this_run = set()
    candidates, dropped = [], []

    def drop(rec, why):
        dropped.append({**rec, "drop_reason": why})

    for rec in listings:
        k = rec.get("key") or make_key(rec["company"], rec["title"])
        rec = {**rec, "key": k}
        st = state.get(k)
        if k in seen_this_run:
            drop(rec, "repeat within this run"); continue
        seen_this_run.add(k)
        if st:
            st["last_seen"] = today
            st["times_seen"] = st.get("times_seen", 1) + 1
        if k in tracker_keys:
            drop(rec, f"already in the tracker ({tracker_keys[k].get('stage', '?')})"); continue
        if st and st.get("first_seen", "") >= cutoff and st.get("verdict"):
            drop(rec, f"already judged {st['first_seen']}: {st['verdict']}"); continue
        c = rec["company"].lower()
        if any(s == c or c.startswith(s + " ") for s in rules["skip_companies"]):
            drop(rec, "ad / gig listing"); continue
        t = rec["title"].lower()
        hit = next((p for p in rules["skip_title_patterns"] if re.search(p, t)), None)
        if hit:
            drop(rec, f"outside target functions (matched '{hit}')"); continue
        # Individual-contributor and entry-level roles (some alert sources send dozens a day).
        # Only when the title carries no leadership word, so a "VP, Sales & Service" or a sales
        # manager still goes on to title triage instead of being dropped here.
        ic = next((p for p in rules.get("skip_ic_title_patterns", []) if re.search(p, t)), None)
        if ic and not any(re.search(p, t) for p in rules["stretch_title_patterns"] + rules["apply_title_patterns"]):
            drop(rec, f"individual-contributor or entry-level role (matched '{ic}')"); continue
        if not location_ok(rec, rules):
            drop(rec, f"on-site outside the commute radius ({rec.get('location')})"); continue
        why, note = pay_verdict(rec, rules)
        if why:
            drop(rec, why); continue
        rec["level"] = level_of(rec["title"], rules)
        rec["screen_note"] = note
        if st:
            rec["repeat_count"] = st.get("times_seen", 1)
        candidates.append(rec)
        state.setdefault(k, {"first_seen": today, "last_seen": today, "times_seen": 1,
                             "company": rec["company"], "title": rec["title"]})

    # Remember every drop too, so tomorrow's copy of the same listing costs nothing. Repeats
    # and "already ..." drops are not new verdicts and must not overwrite the original one.
    for d in dropped:
        state.setdefault(d["key"], {"first_seen": today, "last_seen": today, "times_seen": 1,
                                    "company": d["company"], "title": d["title"]})
        if not state[d["key"]].get("verdict") and not d["drop_reason"].startswith(("already", "repeat")):
            state[d["key"]]["verdict"] = "screened out: " + d["drop_reason"]

    counts = {"listings": len(listings), "candidates": len(candidates), "dropped": len(dropped)}
    by = {}
    for d in dropped:
        r = re.sub(r"\s*\(.*|:.*|\$.*", "", d["drop_reason"]).strip()
        by[r] = by.get(r, 0) + 1
    counts["dropped_by_reason"] = by
    return {"candidates": candidates, "dropped": dropped, "counts": counts}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Rule-based first pass over parsed job listings.")
    ap.add_argument("listings", help="JSON list of parsed listings")
    ap.add_argument("--rules", default=DEFAULT_RULES, help="rules JSON (default: config/rules.example.json)")
    ap.add_argument("--snapshot", help="tracker snapshot JSON: {\"roles\": [{\"company\", \"role\", \"stage\"}]}")
    ap.add_argument("--state", default=ledger.PATH, help="dedupe ledger (read if it exists)")
    ap.add_argument("--write-state", action="store_true", help="save the updated ledger")
    ap.add_argument("--today", help="YYYY-MM-DD (default: today)")
    a = ap.parse_args(argv)
    with open(a.listings, encoding="utf-8") as f:
        listings = json.load(f)
    snap = None
    if a.snapshot:
        with open(a.snapshot, encoding="utf-8") as f:
            snap = json.load(f)
    state = ledger.load(a.state)
    out = screen(listings, load_rules(a.rules), snap, state, a.today)
    if a.write_state:
        ledger.save(state, a.state)
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
    print()


if __name__ == "__main__":
    main()
