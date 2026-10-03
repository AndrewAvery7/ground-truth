# Submit Assistant — a live session with the user (mode B)

Runs only in an interactive session on the user's PC, never in the cloud routine. The user
starts it by saying something like "let's submit today's applications."

## Before touching a browser
1. Pull the latest state and refresh `work/snapshot.json`, then list packages whose
   `CHECK.md` says PASS and whose tracker stage is still Saved. Show the list: company,
   role, score, verdict, pay, apply link.
2. The user picks which to do now. Nothing proceeds for a role they did not name.
3. For each chosen role, re-open `answers.md`. If anything is still **CONFIRM**, ask now
   and write the answer into `config/standard-answers.md` (with today's date) so it is
   never asked twice.

## Per application (in the user's own browser, their own logins)
1. Open the `apply_url` from the package README (employer site; the aggregator's apply
   only when the README says so and the user agreed for that role).
2. If the site needs a sign-in or an account: stop and hand over — **the user signs in or
   creates the account themselves**. Same for any CAPTCHA or email-code check. Never type
   a password.
3. Fill the form from `answers.md` and the resume. Upload the tailored resume PDF (and the
   letter PDF where there is a field for it) from the synced package folder.
4. Questions not in `answers.md`: draft an answer from the master resume and show it
   before entering it. Voluntary self-identification, background-check consent and
   accuracy attestations: the user answers these themselves.
5. On the review page: take a screenshot, summarise what will be sent (files, key
   answers), and ask: **"Submit <Company> — <Role>?"** Press Submit only on a clear yes
   for that role.
6. After submitting: screenshot the confirmation page into the package folder; append
   "Submitted <date> via <ATS>" to the package README; queue the tracker update
   (`stage: Applied`, `applied: today`, `follow: today + 8 days`) and push — keyless
   delivery delivers it. The Clerk also matches the confirmation email next run.

## Never
Submit without a named yes; guess a CONFIRM answer; type a password or solve a CAPTCHA;
apply through board-native "easy apply" automation (platforms ban it); apply to the same
req twice.
