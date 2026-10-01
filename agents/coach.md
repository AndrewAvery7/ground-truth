# Weekly Coach — Sundays

Inputs: this week's `runs/*.md`, `state/seen.json`, and `work/snapshot.json` (roles with
stages and fit scores). Write `runs/weekly-<YYYY>-W<ww>.md`:

1. **The funnel, by source**: listings → candidates → Apply/Stretch → packages → applied →
   responded → interview → offer. Show this week and the running total.
2. **What is working**: response rate by role family and by score band (<50, 50–69, 70+).
   Say plainly when the numbers are too small to mean anything yet (under ~20 applications).
3. **Noise at the source**: which alert streams and search terms produced the most dropped
   listings, and specific alert changes the user could make in the alert provider's own
   settings (they make them; you never touch their account).
4. **Rule tuning**: listings the rules dropped that the Fit Judge would likely have kept,
   or the reverse; propose exact edits to `config/rules.json` / `profile.md` — do not apply
   them.
5. **Warm paths**: companies with an Apply role where a tracker contact exists and no
   outreach is recorded.
6. **Stale**: Applied roles quiet for 14+ days; Saved/High roles older than 5 days.
Keep it to one screen. Lead with the one change that would help most next week.
