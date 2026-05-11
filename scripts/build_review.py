#!/usr/bin/env python3
"""Build a triage-review.md from triaged.csv + verdict-batch CSVs.

Output: each candidate on one line, with current status, source-count, source
types, and auto-flags for brokerage-identity risk (firm-name patterns that
suggest non-brokerage entities). Sections grouped by status so the user can
prune efficiently.
"""
from __future__ import annotations

import csv
import glob
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
CANDIDATES_DIR = os.path.join(ROOT, "candidates")
OUT = os.path.join(ROOT, "triage-review.md")

# Firm-name patterns that suggest non-brokerage entities
RED_FLAG_PATTERNS = [
    (r"\bconsulting\b", "consulting"),
    (r"\badvising\b", "advising"),
    (r"\badvisors\b", "advisors"),
    (r"\bacademy\b", "academy"),
    (r"\bcoaching\b", "coaching"),
    (r"\bmastermind\b", "mastermind"),
    (r"\bcaptive\b", "captive"),
    (r"\bcooperative\b", "cooperative"),
    (r"\bplans\b", "plans"),
    (r"\bcollaboration\b", "collaboration"),
    (r"\bstrategy\b|\bstrategies\b", "strategy"),
    (r"\binstitute\b", "institute"),
    (r"\bnetwork\b", "network"),
    (r"\bin a box\b", "product"),
    (r"\bfiduciary group\b", "401k-fiduciary"),  # often retirement RIA
    (r"\bagency\b", "agency-generic"),  # often P&C-leaning
]

# Patterns that suggest top-100 broker subsidiary (caught at Phase 2 but
# worth re-flagging if any slipped through)
TOP100_PATTERNS = [
    "alera", "nfp", "hub international", "usi", "gallagher", "marsh", "aon",
    "lockton", "brown & brown", "acrisure", "assuredpartners", "risk strategies",
    "onedigital", "higginbotham", "world insurance", "mcgriff", "leavitt",
    "oakbridge", "sunstar", "broadstreet", "foundation risk partners", "alkeme",
    "ima", "pcf", "epic", "hylant", "holmes murphy", "woodruff sawyer",
]


def red_flags(firm: str) -> list[str]:
    f = (firm or "").lower()
    out = []
    for pat, tag in RED_FLAG_PATTERNS:
        if re.search(pat, f):
            out.append(tag)
    for sub in TOP100_PATTERNS:
        if sub in f:
            out.append(f"top100:{sub}")
    return out


def main() -> int:
    # status map by candidate_id from verdict batches
    status: dict[str, dict] = {}
    for vf in sorted(glob.glob(os.path.join(CANDIDATES_DIR, "verdict-batch-*.csv"))):
        with open(vf, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                cid = row["candidate_id"].strip()
                status[cid] = {
                    "verdict": (row.get("verdict") or "").strip().upper(),
                    "firm_size_estimate": row.get("firm_size_estimate", ""),
                    "city": row.get("city", ""),
                    "state": row.get("state", ""),
                    "notes": row.get("notes", ""),
                    "batch": os.path.basename(vf).replace("verdict-batch-", "").replace(".csv", ""),
                }

    # Phase 5 QA dropped c073
    if "c073" in status:
        status["c073"]["verdict"] = "OVERTURNED_QA"

    # leads.csv → map cid → lead_id
    lead_id_map: dict[str, str] = {}
    leads_path = os.path.join(ROOT, "leads.csv")
    if os.path.exists(leads_path):
        with open(leads_path, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                ev = row.get("evidence_file", "")
                cid = os.path.basename(ev).replace(".md", "")
                lead_id_map[cid] = row["lead_id"]

    # Read triaged.csv
    triaged = []
    with open(os.path.join(CANDIDATES_DIR, "triaged.csv"), newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            triaged.append(row)

    # Group
    bucket: dict[str, list] = {
        "VERIFIED": [],
        "INSUFFICIENT_DATA": [],
        "REJECT": [],
        "OVERTURNED_QA": [],
        "UNTOUCHED": [],
    }
    for c in triaged:
        cid = c["candidate_id"]
        st = status.get(cid)
        if st:
            bucket.setdefault(st["verdict"] or "UNKNOWN", []).append((c, st))
        else:
            bucket["UNTOUCHED"].append((c, None))

    # Within UNTOUCHED, sort by source_count desc
    bucket["UNTOUCHED"].sort(key=lambda x: -int(x[0]["source_count"]))

    out: list[str] = []
    out.append("# Triage review — your input requested\n")
    out.append("Mark each line by editing the `[ ]` checkbox or putting `K` (kill — already know / not a brokerage / skip), `V` (verify in next round), or leaving blank (defer).\n")
    out.append("**Auto-flags** in brackets indicate firm-name patterns I want you to double-check (e.g. `consulting`, `advising`, `top100:alera`). They are heuristics, not verdicts.\n")
    out.append("Status legend:")
    out.append("- **VERIFIED** = currently in `leads.csv` (the 28 deliverable). Please mark `K` on any you already know or that aren't really brokerages.")
    out.append("- **INSUFFICIENT_DATA** = met Gates 1/2/4 but failed Gate 3 size (mostly sub-5). Mark `V` to re-evaluate if you'd accept smaller.")
    out.append("- **REJECT** = hard-failed a gate or known excluded. Listed for completeness.")
    out.append("- **UNTOUCHED** = harvested but never verified. Mark `V` on ones you want me to run through Phase 3.\n")
    out.append("---\n")

    def line(c: dict, st: dict | None, *, with_status: bool = False) -> str:
        cid = c["candidate_id"]
        name = c["name"]
        firm = c["firm"]
        n_src = c["source_count"]
        src_types = c["source_types"]
        flags = red_flags(firm)
        flag_str = f"  ⚠️ {','.join(flags)}" if flags else ""
        lead = lead_id_map.get(cid, "")
        prefix = f"{lead} " if lead else ""
        loc = ""
        if st and (st.get("city") or st.get("state")):
            loc = f" — {st.get('city','').strip()}, {st.get('state','').strip()}".rstrip(", ").rstrip()
        size = ""
        if st and st.get("firm_size_estimate"):
            size = f" · size={st['firm_size_estimate']}"
        return f"- [ ] **{prefix}{cid}** {name} | {firm}{loc}{size} | {n_src}× [{src_types}]{flag_str}"

    out.append(f"## VERIFIED — currently in leads.csv ({len(bucket['VERIFIED'])})\n")
    out.append("_Please mark `K` on any you already know personally, have contacted, or that aren't a licensed brokerage. Pay special attention to red-flagged firm names._\n")
    for c, st in sorted(bucket["VERIFIED"], key=lambda x: lead_id_map.get(x[0]["candidate_id"], "Z")):
        out.append(line(c, st))
    out.append("")

    out.append(f"## INSUFFICIENT_DATA — Gates 1/2/4 looked OK, mostly sub-5 size ({len(bucket['INSUFFICIENT_DATA'])})\n")
    out.append("_If you'd relax the size floor to 3, these are the next-best candidates. Mark `V` to re-verify._\n")
    for c, st in bucket["INSUFFICIENT_DATA"]:
        out.append(line(c, st))
    out.append("")

    out.append(f"## UNTOUCHED — never verified ({len(bucket['UNTOUCHED'])})\n")
    out.append("_Sorted by source-triangulation strength (multi-source first). Mark `V` to put through Phase 3._\n")

    # Sub-group untouched by source count tier
    cur_tier = None
    for c, st in bucket["UNTOUCHED"]:
        sc = int(c["source_count"])
        tier_label = (
            f"### {sc} source(s)" if sc != cur_tier
            else None
        )
        if tier_label:
            out.append("")
            out.append(tier_label + "\n")
            cur_tier = sc
        out.append(line(c, st))
    out.append("")

    out.append(f"## REJECT — already failed, listed for completeness ({len(bucket['REJECT'])})\n")
    out.append("<details>\n<summary>Click to expand (mostly known top-100 subsidiaries, non-brokerages, employees)</summary>\n")
    for c, st in bucket["REJECT"]:
        out.append(line(c, st))
    out.append("</details>\n")

    if bucket.get("OVERTURNED_QA"):
        out.append(f"## OVERTURNED by QA ({len(bucket['OVERTURNED_QA'])})\n")
        for c, st in bucket["OVERTURNED_QA"]:
            out.append(line(c, st))
        out.append("")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")

    # Stats
    print(f"Wrote {OUT}")
    for k, v in bucket.items():
        print(f"  {k}: {len(v)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
