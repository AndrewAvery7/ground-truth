import json
import os

import pytest

from groundtruth.screen import load_rules, make_key, screen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-10-01"


@pytest.fixture
def rules():
    return load_rules(os.path.join(ROOT, "config", "rules.example.json"))


@pytest.fixture
def listings():
    with open(os.path.join(ROOT, "examples", "listings.json"), encoding="utf-8") as f:
        return json.load(f)


def run(listings, rules, **kw):
    out = screen(listings, rules, today=TODAY, **kw)
    kept = {c["company"]: c for c in out["candidates"]}
    dropped = {d["company"]: d["drop_reason"] for d in out["dropped"]}
    return out, kept, dropped


def test_keeps_exactly_the_keepers(listings, rules):
    out, kept, dropped = run(listings, rules)
    assert set(kept) == {"Harborview Logistics", "Granite Ridge Supply",
                         "Northgate Fulfillment", "Summit Parcel Co."}
    assert out["counts"]["listings"] == len(listings)
    assert out["counts"]["candidates"] + out["counts"]["dropped"] == len(listings)


def test_every_rule_drops_its_listing(listings, rules):
    _, _, dropped = run(listings, rules)
    assert dropped["QuickShift Gigs"] == "ad / gig listing"
    assert dropped["Harborview Logistics, Inc."] == "repeat within this run"
    assert dropped["Lakeshore Freight Partners"].startswith("employer pay tops out at $92,000")
    assert dropped["Pinecrest Cold Chain"].startswith("on-site outside the commute radius")
    assert dropped["Meridian Route Systems"].startswith("outside target functions")
    assert dropped["Copperline Logistics"].startswith("site-a estimate tops out at $88,000")
    assert dropped["Riverbend Carriers"].startswith("individual-contributor or entry-level role")


def test_keepers_are_labelled_not_judged(listings, rules):
    _, kept, _ = run(listings, rules)
    assert kept["Harborview Logistics"]["level"] == "apply"
    assert kept["Harborview Logistics"]["screen_note"] == ""
    assert kept["Granite Ridge Supply"]["screen_note"] == "below target pay"      # flagged band
    assert kept["Northgate Fulfillment"]["level"] == "stretch"
    assert kept["Northgate Fulfillment"]["screen_note"] == "pay not shown"        # unknown pay keeps
    assert kept["Summit Parcel Co."]["level"] == "apply"                           # "3 Locations" keeps


def test_key_collapses_suffixes_and_remote_markers():
    assert make_key("Harborview Logistics, Inc.", "Director of Distribution Operations - Remote") == \
        make_key("Harborview Logistics", "Director of Distribution Operations")


def test_leadership_word_saves_a_sales_title(rules):
    rec = {"company": "Riverbend Carriers", "title": "Vice President, Sales Specialist Teams",
           "remote": True}
    out, kept, _ = run([rec], rules)
    assert kept["Riverbend Carriers"]["level"] == "stretch"


def test_override_pattern_wins_over_stretch(rules):
    # The example rules ship with no overrides; a user who needs one adds a pattern.
    rules = {**rules, "apply_override_patterns": [r"\bvice president of field operations\b"]}
    rec = {"company": "Harborview Logistics", "title": "Vice President of Field Operations",
           "location": "Columbus, OH"}
    _, kept, _ = run([rec], rules)
    assert kept["Harborview Logistics"]["level"] == "apply"
    plain = {"company": "Harborview Logistics", "title": "Vice President, Operations",
             "location": "Columbus, OH"}
    _, kept2, _ = run([plain], {**rules, "apply_override_patterns": []})
    assert kept2["Harborview Logistics"]["level"] == "stretch"


def test_tracker_snapshot_and_ledger_dedupe(listings, rules):
    snapshot = {"roles": [{"company": "Summit Parcel Company", "role": "Director, Warehouse Operations",
                           "stage": "Applied"}]}
    state = {}
    _, _, dropped = run(listings, rules, snapshot=snapshot, state=state)
    assert dropped["Summit Parcel Co."] == "already in the tracker (Applied)"
    # Drops are remembered with a verdict; repeats are not re-verdicted.
    k = make_key("Lakeshore Freight Partners", "Senior Manager, Warehouse Operations")
    assert state[k]["verdict"].startswith("screened out: employer pay")
    # The next run skips anything already judged within dedupe_days.
    state[make_key("Harborview Logistics", "Director of Distribution Operations")]["verdict"] = "Apply: 81"
    _, kept, dropped = run(listings, rules, state=state)
    assert "Harborview Logistics" not in kept
    assert dropped["Harborview Logistics"].startswith("already judged")
