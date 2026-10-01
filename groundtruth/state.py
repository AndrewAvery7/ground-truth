"""The dedupe ledger: record what the Fit Judge (or the user) decided about a listing, so it
is never judged twice.

The ledger is one JSON object keyed by listing key ("<company>|<title>", normalised by
``groundtruth.screen.make_key``). The screener reads and updates it on every run; this
command lets an agent or a person record a verdict by hand.

    python -m groundtruth.state set "<key>" --verdict "Apply: 78, strong network-ops match" [--tracker-id t123]
    python -m groundtruth.state get "<key>"
"""
import argparse
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "state", "seen.json")


def load(path=PATH):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(state, path=PATH):
    """Write atomically: a crash mid-write must never leave a half-written ledger."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["set", "get"])
    ap.add_argument("key")
    ap.add_argument("--verdict")
    ap.add_argument("--tracker-id", help="the role's id in your tracker, if it has one")
    ap.add_argument("--path", default=PATH)
    a = ap.parse_args(argv)
    st = load(a.path)
    if a.cmd == "get":
        json.dump(st.get(a.key), sys.stdout, indent=1)
        return
    rec = st.setdefault(a.key, {"first_seen": dt.date.today().isoformat(), "times_seen": 1})
    if a.verdict:
        rec["verdict"] = a.verdict
        rec["judged"] = dt.date.today().isoformat()
    if a.tracker_id:
        rec["tracker_id"] = a.tracker_id
    save(st, a.path)
    print(json.dumps(rec))


if __name__ == "__main__":
    main()
