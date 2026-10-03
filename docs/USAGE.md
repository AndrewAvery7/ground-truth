# Ground Truth — the code

Two pieces of the pipeline are deterministic code, not a model, and they ship here as a
small, runnable Python package (standard library only; `pytest` for the tests):

- **`groundtruth.screen`** — the Screener. Drops only the unambiguous misses (ads and gig
  work, repeats, roles already tracked or judged, pay below the floor, on-site outside the
  commute radius, wrong functions) and labels the rest with a level. *A wrong drop here is
  invisible forever; a wrong keep costs one lookup.*
- **`groundtruth.check`** — the Checker's mechanical pass. Every figure in a tailored
  resume must appear in the master resume, no retired claim may reappear, and employer,
  title, date and education lines must be word-for-word. Any error is a HOLD that names the
  line.
- **`groundtruth.state`** — the dedupe ledger both of them rely on.

All example data is for a fictional persona, Mark Callahan (operations leader, third-party
logistics, Columbus OH). Every employer in `examples/` is invented.

## Run it

Python 3.9+. On Windows, set `PYTHONUTF8=1` first.

```
python -m groundtruth.screen examples/listings.json --rules config/rules.example.json
python -m groundtruth.check examples/tailored-draft.md --master examples/master-resume.md --retired examples/retired-claims.txt
python -m pytest -q
```

Your own rules go in a copy of `config/rules.example.json`; its `_comment` key explains each
field. The screener reads and (with `--write-state`) updates a ledger at `state/seen.json`;
`--snapshot` takes your tracker's current roles so nothing already tracked comes back.

## Sample output

The README shows both commands run on the examples, with a one-line-per-listing summary
of the screener and the checker's HOLD verdict. The screener's complete JSON for the same
run (`--today 2026-10-01`):

<details><summary>Full screener output</summary>

```json
{
 "candidates": [
  {
   "company": "Harborview Logistics",
   "title": "Director of Distribution Operations",
   "pay_min": 142000,
   "pay_max": 168000,
   "pay_estimated": false,
   "remote": false,
   "location": "Columbus, OH",
   "posted": "2 days ago",
   "source": "site-a",
   "key": "harborview logistics|director of distribution operations",
   "level": "apply",
   "screen_note": ""
  },
  {
   "company": "Granite Ridge Supply",
   "title": "Director, Continuous Improvement",
   "pay_min": 112000,
   "pay_max": 123000,
   "pay_estimated": false,
   "remote": false,
   "location": "Dublin, OH",
   "posted": "5 days ago",
   "source": "site-a",
   "key": "granite ridge supply|director continuous improvement",
   "level": "apply",
   "screen_note": "below target pay"
  },
  {
   "company": "Northgate Fulfillment",
   "title": "Vice President, Network Strategy",
   "pay_min": null,
   "pay_max": null,
   "pay_estimated": false,
   "remote": true,
   "location": "Remote (US)",
   "posted": "1 day ago",
   "source": "site-b",
   "key": "northgate fulfillment|vice president network strategy",
   "level": "stretch",
   "screen_note": "pay not shown"
  },
  {
   "company": "Summit Parcel Co.",
   "title": "Director, Warehouse Operations",
   "pay_min": 138000,
   "pay_max": 158000,
   "pay_estimated": false,
   "remote": false,
   "location": "3 Locations",
   "posted": "3 days ago",
   "source": "site-b",
   "key": "summit parcel|director warehouse operations",
   "level": "apply",
   "screen_note": ""
  }
 ],
 "dropped": [
  {
   "company": "QuickShift Gigs",
   "title": "Delivery Driver - Earn Weekly, Start Today",
   "pay_min": null,
   "pay_max": null,
   "pay_estimated": false,
   "remote": false,
   "location": "Columbus, OH",
   "posted": "today",
   "source": "site-a",
   "key": "quickshift gigs|delivery driver earn weekly start today",
   "drop_reason": "ad / gig listing"
  },
  {
   "company": "Harborview Logistics, Inc.",
   "title": "Director of Distribution Operations - Remote",
   "pay_min": 142000,
   "pay_max": 168000,
   "pay_estimated": false,
   "remote": false,
   "location": "Columbus, OH",
   "posted": "3 days ago",
   "source": "site-b",
   "key": "harborview logistics|director of distribution operations",
   "drop_reason": "repeat within this run"
  },
  {
   "company": "Lakeshore Freight Partners",
   "title": "Senior Manager, Warehouse Operations",
   "pay_min": 78000,
   "pay_max": 92000,
   "pay_estimated": false,
   "remote": false,
   "location": "Grove City, OH",
   "posted": "1 week ago",
   "source": "site-a",
   "key": "lakeshore freight partners|senior manager warehouse operations",
   "drop_reason": "employer pay tops out at $92,000 (below $120,000)"
  },
  {
   "company": "Pinecrest Cold Chain",
   "title": "Director of Operations",
   "pay_min": 155000,
   "pay_max": 178000,
   "pay_estimated": false,
   "remote": false,
   "location": "Phoenix, AZ",
   "posted": "4 days ago",
   "source": "site-b",
   "key": "pinecrest cold chain|director of operations",
   "drop_reason": "on-site outside the commute radius (Phoenix, AZ)"
  },
  {
   "company": "Meridian Route Systems",
   "title": "Senior Software Engineer, Routing",
   "pay_min": 160000,
   "pay_max": 190000,
   "pay_estimated": false,
   "remote": true,
   "location": "Remote (US)",
   "posted": "2 days ago",
   "source": "site-a",
   "key": "meridian route systems|senior software engineer routing",
   "drop_reason": "outside target functions (matched '\\bsoftware engineer\\b')"
  },
  {
   "company": "Copperline Logistics",
   "title": "Director of Transportation",
   "pay_min": 72000,
   "pay_max": 88000,
   "pay_estimated": true,
   "remote": false,
   "location": "Westerville, OH",
   "posted": "6 days ago",
   "source": "site-a",
   "key": "copperline logistics|director of transportation",
   "drop_reason": "site-a estimate tops out at $88,000 (below $110,000)"
  },
  {
   "company": "Riverbend Carriers",
   "title": "Freight Sales Representative",
   "pay_min": 55000,
   "pay_max": 70000,
   "pay_estimated": false,
   "remote": false,
   "location": "Columbus, OH",
   "posted": "today",
   "source": "site-b",
   "key": "riverbend carriers|freight sales representative",
   "drop_reason": "individual-contributor or entry-level role (matched '\\bsales representative\\b')"
  }
 ],
 "counts": {
  "listings": 11,
  "candidates": 4,
  "dropped": 7,
  "dropped_by_reason": {
   "ad / gig listing": 1,
   "repeat within this run": 1,
   "employer pay tops out at": 1,
   "on-site outside the commute radius": 1,
   "outside target functions": 1,
   "site-a estimate tops out at": 1,
   "individual-contributor or entry-level role": 1
  }
 }
}
```

</details>

## What the checker does not do

It reads plain text or Markdown, so it cannot count pages: render the final documents and
check their length yourself. And it is only the first pass: the Checker agent then reads
every sentence beside the master for claims stretched in wording ("led" where the master
says "partnered"), which no rule can see.
