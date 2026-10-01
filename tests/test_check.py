import os

from groundtruth.check import check

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "examples")
MASTER = os.path.join(EX, "master-resume.md")
RETIRED = os.path.join(EX, "retired-claims.txt")
DRAFT = os.path.join(EX, "tailored-draft.md")
BAD_LINE = "Built and led a 40-person team"


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return str(p)


def test_unsupported_team_size_is_held_and_cites_the_line():
    out = check(DRAFT, master=MASTER, retired=RETIRED)
    assert out["verdict"] == "HOLD" and out["pass"] is False
    assert len(out["errors"]) == 1
    assert "figure not in the master: 40" in out["errors"][0]
    assert BAD_LINE in out["errors"][0]


def test_passes_once_the_line_is_removed(tmp_path):
    fixed = "\n".join(l for l in read(DRAFT).splitlines() if BAD_LINE not in l)
    out = check(write(tmp_path, "fixed.md", fixed), master=MASTER, retired=RETIRED)
    assert out["verdict"] == "PASS", out["errors"]
    assert out["retired_list_size"] == 3


def test_master_checks_clean_against_itself():
    assert check(MASTER, master=MASTER, retired=RETIRED)["verdict"] == "PASS"


def test_retired_claim_is_held_even_without_a_new_figure(tmp_path):
    text = read(DRAFT).replace(BAD_LINE + " across network operations and analytics.",
                               "Certified Lean Six Sigma Black Belt.")
    out = check(write(tmp_path, "retired.md", text), master=MASTER, retired=RETIRED)
    assert out["verdict"] == "HOLD"
    assert any("retired claim: 'Lean Six Sigma Black Belt'" in e and "Certified" in e
               for e in out["errors"])


def test_altered_protected_line_is_held(tmp_path):
    text = read(DRAFT).replace("Sr. Director, Network Operations", "Vice President, Network Operations")
    text = "\n".join(l for l in text.splitlines() if BAD_LINE not in l)
    out = check(write(tmp_path, "title.md", text), master=MASTER, retired=RETIRED)
    assert out["verdict"] == "HOLD"
    assert any(e.startswith("protected line altered or removed") for e in out["errors"])


def test_changed_contact_line_and_leftover_markup_are_held(tmp_path):
    text = read(DRAFT).replace("Columbus, Ohio", "Dayton, Ohio").replace("Own the $46M", "Own the **$46M**")
    text = "\n".join(l for l in text.splitlines() if BAD_LINE not in l)
    out = check(write(tmp_path, "contact.md", text), master=MASTER, retired=RETIRED)
    errs = " ".join(out["errors"])
    assert "contact line changed or missing" in errs
    assert "placeholder or leftover markup" in errs


def test_letter_rules(tmp_path):
    header = ["Mark Callahan", "Columbus, Ohio", "October 1, 2026", "Hiring Team",
              "Harborview Logistics", "Columbus, OH", "Dear Hiring Team,"]
    body = ("I run distribution networks the way Harborview runs its lanes: by the numbers. "
            "At Ridgeline Distribution I own a $46M linehaul P&L and consolidated a 6-site "
            "network for $18M in validated savings. ") * 7
    letter = write(tmp_path, "letter.md", "\n".join(header + [body, "Mark Callahan"]))
    fixed = "\n".join(l for l in read(DRAFT).splitlines() if BAD_LINE not in l)
    resume = write(tmp_path, "fixed.md", fixed)
    ok = check(resume, letter=letter, company="Harborview Logistics", master=MASTER, retired=RETIRED)
    assert ok["verdict"] == "PASS", ok["errors"]
    held = check(resume, letter=letter, company="Northgate Fulfillment", master=MASTER, retired=RETIRED)
    assert any("never names the company" in e for e in held["errors"])
