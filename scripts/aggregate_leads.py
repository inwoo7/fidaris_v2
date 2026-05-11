#!/usr/bin/env python3
"""Phase 4: aggregate VERIFIED verdicts into leads.csv with rich fields from evidence files."""
from __future__ import annotations

import csv
import glob
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
CANDIDATES_DIR = os.path.join(ROOT, "candidates")
EVIDENCE_DIR = os.path.join(ROOT, "evidence")
OUT_CSV = os.path.join(ROOT, "leads.csv")


def split_name(full: str) -> tuple[str, str]:
    full = (full or "").strip()
    parts = full.split()
    if len(parts) == 0:
        return ("", "")
    if len(parts) == 1:
        return (parts[0], "")
    # Handle "Jr.", "Sr.", "III" suffixes
    suffix = ""
    if parts[-1].rstrip(".").lower() in {"jr", "sr", "ii", "iii", "iv"}:
        suffix = " " + parts[-1]
        parts = parts[:-1]
    if len(parts) == 1:
        return (parts[0], suffix.strip())
    return (parts[0], " ".join(parts[1:]) + suffix)


def extract_section(text: str, header: str) -> str:
    """Extract markdown section under a `## <header>` line until next `## ` or EOF."""
    m = re.search(rf"^## {re.escape(header)}.*?$(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ""


def extract_field(text: str, label: str) -> str:
    """Extract a bolded label like **City/State:** value."""
    m = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(.+?)\s*$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def summarize_gate(section: str, max_chars: int = 600) -> str:
    """Reduce a gate section to its source-bullet lines, joined with ' | '."""
    bullets = [ln.strip("- ").strip() for ln in section.splitlines() if ln.strip().startswith("- ")]
    out = " | ".join(bullets)
    if len(out) > max_chars:
        out = out[: max_chars - 1] + "…"
    return out


def warmth_from_notes(notes_section: str) -> str:
    m = re.search(r"[Ww]armth\s*(?:score)?[:\s]+(\d)", notes_section)
    return m.group(1) if m else ""


def intro_path_from_notes(notes_section: str) -> str:
    # find the bullet starting with "Best intro path" or similar
    m = re.search(r"-\s*Best intro path[^\n]*", notes_section)
    if m:
        return m.group(0).lstrip("- ").strip()
    # fallback: first non-warmth, non-yellow-flag bullet
    for ln in notes_section.splitlines():
        s = ln.strip().lstrip("- ").strip()
        if s and not s.lower().startswith(("warmth", "yellow flag")):
            return s
    return ""


def main() -> int:
    # Collect verdict rows
    verdict_files = sorted(glob.glob(os.path.join(CANDIDATES_DIR, "verdict-batch-*.csv")))
    verified: dict[str, dict] = {}

    for vf in verdict_files:
        with open(vf, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if (row.get("verdict") or "").strip().upper() == "VERIFIED":
                    cid = row["candidate_id"].strip()
                    if cid in verified:
                        # Duplicate verification — keep the first occurrence, log
                        print(f"WARN: duplicate VERIFIED for {cid} in {vf}", file=sys.stderr)
                        continue
                    verified[cid] = {"src_batch": os.path.basename(vf), **row}

    # Drop intra-deliverable dupes (same person, different cIDs) — known list:
    # c032 was consolidated into c017 by the verifier; c042 dup of c002 (Contorno); etc.
    known_dupe_drops = {
        "c032",  # Carl Schuessler Jr (kept c017)
        "c042",  # Contorno (kept c002)
        "c043",  # Silverman (kept c035 — actually c035 was REJECT)
        "c046",  # Griswold (kept c041 — both REJECT anyway)
        "c051",  # Tom DiLiegro (kept c044)
        "c066",  # Louis Bernardi (kept c033)
    }
    for k in list(verified.keys()):
        if k in known_dupe_drops:
            print(f"INFO: dropping known dupe {k}", file=sys.stderr)
            del verified[k]

    rows_out: list[dict] = []
    for i, (cid, row) in enumerate(sorted(verified.items(), key=lambda kv: int(kv[0].lstrip("c")))):
        lead_id = f"L{i+1:02d}"
        ev_path = os.path.join(EVIDENCE_DIR, f"{cid}.md")
        ev_text = ""
        if os.path.exists(ev_path):
            with open(ev_path, encoding="utf-8") as fh:
                ev_text = fh.read()

        first, last = split_name(row["name"])
        city = row.get("city", "")
        state = row.get("state", "")
        if not city or not state:
            cs = extract_field(ev_text, "City/State")
            if cs and "," in cs:
                ccity, cstate = [p.strip() for p in cs.split(",", 1)]
                city = city or ccity
                state = state or cstate

        linkedin = row.get("linkedin_url", "") or extract_field(ev_text, "LinkedIn URL")
        website = row.get("firm_website", "") or extract_field(ev_text, "Firm website")

        gate1_section = extract_section(ev_text, "Gate 1: Owner status")
        gate2_section = extract_section(ev_text, "Gate 2: Fiduciary alignment")
        gate3_section = extract_section(ev_text, "Gate 3: Firm size (target 5-15)")
        gate4_section = extract_section(ev_text, "Gate 4: Self-funded book")
        notes_section = extract_section(ev_text, "Notes")

        # Derive title (best-effort) from Gate 1 snippet
        title = ""
        for kw in ("Founder", "Co-Founder", "President", "CEO", "Managing Partner", "Principal", "Owner"):
            if re.search(rf"\b{kw}\b", gate1_section):
                title = kw
                break

        rows_out.append({
            "lead_id": lead_id,
            "first_name": first,
            "last_name": last,
            "title": title,
            "firm_name": row["firm"],
            "firm_website": website,
            "linkedin_url": linkedin,
            "city": city,
            "state": state,
            "firm_size_estimate": row.get("firm_size_estimate", ""),
            "firm_size_sources": summarize_gate(gate3_section, 400),
            "fiduciary_signals": summarize_gate(gate2_section, 500),
            "self_funded_evidence": summarize_gate(gate4_section, 500),
            "owner_evidence": summarize_gate(gate1_section, 400),
            "podcast_appearances": "",  # not separately extracted; in notes/gate 2
            "authored_content": "",
            "notable_clients_or_case_studies": "",
            "contact_email_if_public": "",
            "contact_phone_if_public": "",
            "warmth_score_1_to_5": warmth_from_notes(notes_section),
            "intro_path_ideas": intro_path_from_notes(notes_section),
            "evidence_file": f"evidence/{cid}.md",
        })

    fieldnames = [
        "lead_id", "first_name", "last_name", "title", "firm_name", "firm_website", "linkedin_url",
        "city", "state", "firm_size_estimate", "firm_size_sources", "fiduciary_signals",
        "self_funded_evidence", "owner_evidence", "podcast_appearances", "authored_content",
        "notable_clients_or_case_studies", "contact_email_if_public", "contact_phone_if_public",
        "warmth_score_1_to_5", "intro_path_ideas", "evidence_file",
    ]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows_out)

    print(f"Wrote {len(rows_out)} verified leads to {OUT_CSV}", file=sys.stderr)
    print("\nVerified leads:", file=sys.stderr)
    for r in rows_out:
        print(f"  {r['lead_id']} | {r['first_name']} {r['last_name']} | {r['firm_name']} | {r['city']}, {r['state']} | size={r['firm_size_estimate']} | warmth={r['warmth_score_1_to_5']}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
