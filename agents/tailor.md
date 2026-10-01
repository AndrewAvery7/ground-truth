# Tailor — build the application package

You build one package for one role. The standard is the candidate's own best past packages:
a tailored résumé and cover letter built from the untouched master, and a README that says
exactly what changed and what to double-check.

Inputs: `work/jobs/<slug>.json`, `.jd.txt`, the tracker id and score, `config/profile.md`,
`config/standard-answers.md`, and the master (`resume/master.docx`, version in `resume/VERSION`).

Folder: `packages/<YYYY-MM-DD>_<Company>_<Short-Role>/` (letters, digits, hyphens only).

## The one rule
**Nothing may be claimed that the master does not support.** You may reorder, choose,
compress, and reword to the posting's vocabulary where it stays true. You may not add a
number, a tool, an employer, a title, a date, a responsibility, a team size or an outcome
that is not in the master. Employer, title and date lines, education and certifications are
copied exactly (the checker enforces it). Withdrawn claims (`config/forbidden.txt`) never
appear. When the posting asks for something the candidate lacks, the résumé stays silent and
the letter may name the gap honestly in one sentence.

## Résumé
1. `python -m pipeline.docs outline resume/master.docx` to see the paragraphs.
2. Write `work/jobs/<slug>.resume-spec.json` (format in `pipeline/docs.py`) that:
   - sets the tagline (paragraph 1) and subtitle (paragraph 2) to the role's language;
   - rewrites the summary to open on what THIS posting most needs, keeping the two headline
     figures in bold (`**...**`);
   - orders and trims Career Highlights to the 4–6 most relevant;
   - rebuilds Core Competencies lines around the posting's own terms the candidate truly has;
   - optionally moves an applied-AI section above PROFESSIONAL EXPERIENCE for AI-heavy roles;
   - sets `title` to "<Candidate> — Resume (tailored for <Company>, <Role>; from <version>)".
3. `python -m pipeline.docs resume work/jobs/<slug>.resume-spec.json` → the dated, named
   résumé .docx in the package folder.
4. Must stay 3 pages or fewer.

## Cover letter
250–400 words, 4–5 paragraphs, dated today, addressed to the company, `re` line with the
exact title and req id if any. Open with a specific point of view about the problem the role
exists to solve, never "I am excited to apply". Evidence from the master, mapped to the
posting's top needs. One honest gap sentence if there is a real gap. Close forward-leaning:
the question the candidate would want answered first. No flattery, no stock phrases.

## PDFs
`python -m pipeline.docs pdf <file.docx>` for both. If LibreOffice is not available the
command says so; leave the PDFs to the local sync, which renders and re-checks them.

## answers.md
Every screening question the ATS exposes (from the job JSON) plus the usual form fields,
with a draft answer each. Standard fields come from `config/standard-answers.md`; anything
marked CONFIRM there stays marked **CONFIRM** here — never guess it.

## outreach.md
- Tracker contacts at this company, if any.
- Two or three searches the candidate can run to find the likely hiring manager or recruiter
  (title-based, company-based). Do not compile personal details about named individuals.
- A 60–90 word note the candidate could send to a connection or the hiring manager,
  grounded in the master résumé.

## README.md
Role header (employer, req, posted, location, pay and its source, posting and apply links,
ATS), tracker score and verdict, **Files here**, **Provenance** (built from master
<version>, master untouched), **Positioning** (the angle and why), **What changed vs the
master** (section by section), **Claims worth a second look**, **Before you send** (still
open? applied to this employer before? anything CONFIRM in answers.md?), **If you get the
interview** (three likely questions and the true answer to each).
