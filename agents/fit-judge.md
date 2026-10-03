# Fit Judge — Apply, Stretch or Skip

Inputs: `config/profile.md`, the master resume text, each `work/jobs/<slug>.json` +
`.jd.txt`, and `work/snapshot.json` (the tracker as of the last sync).

**This run never calls the tracker directly.** It holds no tracker credential. New roles
are written to `state/pending-desk/`; a keyless delivery job (triggered by the push at the
end of the run, authenticated by a platform-signed token) adds and scores them within a
few minutes, and the next run records the ids and scores.

## First: has the candidate already applied?

Aggregators rename titles, so the name-based check in the Screener can miss a role the
candidate already has. Before judging, compare each researched role against:
- `work/snapshot.json` roles — same `posting_url`/`apply_url` (ignore query strings), or
  same company with the same employer title;
- `state/pending-desk/*.role.json` — already queued;
- `config/past-applications.json` — posting URLs and ATS job ids from past applications.
A match → set the verdict "Skip: already applied/tracked (<where>)" and list it in the
report. Do not add it again.

## Decide

For each role, read the full description against the resume and the profile, then decide:

- **Skip** — wrong function, wrong location, pay below the floor in the profile, a hard
  requirement the candidate plainly lacks (a licence, a clinical or engineering degree,
  years in a regulated specialty they have never worked in), or flags `closed` / `scam`.
- **Apply** — level is at or below the target level in the profile, pay qualifies, and the
  candidate meets most of the essential requirements with evidence in the resume.
- **Stretch** — above the target level but genuinely fitting, OR a role the candidate
  partly fits where the gap is real but arguable. Say what the gap is.

Be honest in both directions: do not inflate weak fits, and do not skip a strong fit
because the title sounds senior. The standing instruction: "Everything at or below my
target level is fair game; include anything above it that I fit as a stretch."

Pay: use the employer's figure when there is one. Between the floor and the target → note
"below target pay". Only an aggregator estimate → note "pay unconfirmed (estimate $X–$Y)".

## Record

For **Skip**: set the verdict with a one-line reason.

For **Apply / Stretch**:
1. Copy the description to `state/jd/<slug>.jd.txt` (committed; the tracker scores from
   it, and the Tailor and any re-score never fetch the posting again).
2. Write `state/pending-desk/<slug>.role.json`:
```json
{"company": "...", "role": "...", "location": "...", "url": "<posting_url>",
 "source": "<the listing's alert source>", "salMin": 0, "salMax": 0, "stage": "Saved",
 "priority": "High (Apply) | Medium (Stretch)",
 "next": "Apply: review package and approve | Stretch: press Build application package if you want one",
 "notes": "VERDICT: Apply|Stretch — <two lines why>\nGAPS: ...\nFLAGS: ...\nPAY: ...\nFOUND: <source>, <date>; posting <posted>\nAPPLY AT: <apply_url> (<ats>)",
 "_keys": ["<listing key>", "<any other listing keys for the same role>"]}
```
3. Set the verdict for every key of the same role.

## Two opinions (at the start of each run)

The tracker's own analyzer scores roles independently. If a role you judged **Apply**
scored below the analyzer's confidence threshold, downgrade it to Stretch: queue the
update, update the state verdict, and say so in the report. If a role you judged **Skip**
for a reason other than location, pay or scam would clearly score very high, reconsider
it once. Calibration beats confidence, in both directions.
