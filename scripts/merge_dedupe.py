#!/usr/bin/env python3
"""Phase 2: merge all raw-*.csv harvests, dedupe by (name, firm), apply exclusion list."""
from __future__ import annotations

import csv
import glob
import os
import re
import sys
from collections import defaultdict

CANDIDATES_DIR = os.path.join(os.path.dirname(__file__), "..", "candidates")

# Seed exclusion list inferred from brief (user confirmed: seed-only, flag dupes at Phase 4)
EXCLUDED_PEOPLE = {
    ("justin", "leader"),
    ("brian", "uhlig"),
    ("anna", "maria"),
    ("jeff", "hogan"),
    ("sean", "schantzen"),
    ("erik", "davis"),
    ("autumn", "yongchu"),
    ("dan", "marshall"),
    ("will", "johnson"),
    ("sam", "wiener"),
}
EXCLUDED_FIRMS_SUBSTR = {
    "benefitsdna",
    "alera",
    "judi group",
    "health rosetta",  # the org itself, not an advisor's firm
    "guide health",
    "gyde",
}

# Top-100 national brokers / PE rollups — drop any candidate at one of these (case-insensitive substring)
TOP_NATIONAL_BROKERS = {
    "marsh", "aon", "lockton", "alera", "nfp", "usi", "hub international",
    "gallagher", "willis towers watson", "willis", "mercer", "brown & brown",
    "brown and brown", "onedigital", "higginbotham", "acrisure",
    "assuredpartners", "risk strategies", "epic", "hylant", "ima",
    "holmes murphy", "woodruff sawyer", "mcgriff", "pcf insurance",
    "north risk", "aia", "ingroup", "frost insurance", "cottingham & butler",
    "cobbs allen", "rcm&d", "kapnick", "alliant", "world insurance",
}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def name_key(name: str) -> tuple[str, str]:
    """Return (first, last) lowercased, last-token used as 'last'."""
    n = norm(name)
    parts = n.split()
    if not parts:
        return ("", "")
    if len(parts) == 1:
        return (parts[0], "")
    return (parts[0], parts[-1])


def firm_key(firm: str) -> str:
    f = norm(firm)
    # strip common suffixes
    f = re.sub(r"\b(llc|inc|inc\.|incorporated|llp|ltd|co\.|corp|corporation|group|insurance|benefits|consulting|consultants|advisors|partners|advisory)\b", "", f)
    f = re.sub(r"[^\w\s]", " ", f)
    f = re.sub(r"\s+", " ", f).strip()
    return f


def is_excluded(name: str, firm: str) -> str | None:
    nk = name_key(name)
    if nk in EXCLUDED_PEOPLE:
        return f"exclusion-list:person:{nk[0]} {nk[1]}"
    f = norm(firm)
    for sub in EXCLUDED_FIRMS_SUBSTR:
        if sub in f:
            return f"exclusion-list:firm-substr:{sub}"
    for big in TOP_NATIONAL_BROKERS:
        if big in f:
            return f"top-national-broker:{big}"
    return None


def main() -> int:
    raw_files = sorted(glob.glob(os.path.join(CANDIDATES_DIR, "raw-*.csv")))
    print(f"Found {len(raw_files)} raw files.", file=sys.stderr)

    merged: dict[tuple, dict] = {}
    excluded_log: list[dict] = []
    n_in = 0

    for path in raw_files:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                n_in += 1
                name = row.get("name", "").strip()
                firm = row.get("firm", "").strip()
                if not name:
                    continue

                reason = is_excluded(name, firm)
                if reason:
                    excluded_log.append({
                        "name": name, "firm": firm,
                        "source_url": row.get("source_url", ""),
                        "source_type": row.get("source_type", ""),
                        "exclusion_reason": reason,
                    })
                    continue

                key = (name_key(name), firm_key(firm))
                if key in merged:
                    rec = merged[key]
                    rec["sources"].append({
                        "url": row.get("source_url", ""),
                        "type": row.get("source_type", ""),
                        "reason": row.get("reason", ""),
                    })
                else:
                    merged[key] = {
                        "name": name,
                        "firm": firm,
                        "sources": [{
                            "url": row.get("source_url", ""),
                            "type": row.get("source_type", ""),
                            "reason": row.get("reason", ""),
                        }],
                    }

    # Write triaged.csv
    out_path = os.path.join(CANDIDATES_DIR, "triaged.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([
            "candidate_id", "name", "firm", "source_count",
            "source_types", "source_urls", "reasons",
        ])
        for i, (key, rec) in enumerate(sorted(merged.items(), key=lambda kv: -len(kv[1]["sources"]))):
            cid = f"c{i+1:03d}"
            types = "; ".join(sorted({s["type"] for s in rec["sources"] if s["type"]}))
            urls = " | ".join(s["url"] for s in rec["sources"] if s["url"])
            reasons = " | ".join(s["reason"] for s in rec["sources"] if s["reason"])
            w.writerow([
                cid, rec["name"], rec["firm"], len(rec["sources"]),
                types, urls, reasons,
            ])

    # Write excluded log
    excl_path = os.path.join(CANDIDATES_DIR, "excluded.csv")
    with open(excl_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "name", "firm", "source_url", "source_type", "exclusion_reason",
        ])
        w.writeheader()
        w.writerows(excluded_log)

    print(f"Input rows:              {n_in}", file=sys.stderr)
    print(f"Excluded (seed+rollups): {len(excluded_log)}", file=sys.stderr)
    print(f"Unique candidates:       {len(merged)}", file=sys.stderr)
    print(f"Output:                  {out_path}", file=sys.stderr)
    print(f"Excluded log:            {excl_path}", file=sys.stderr)

    # Distribution by source-count
    by_count: dict[int, int] = defaultdict(int)
    for rec in merged.values():
        by_count[len(rec["sources"])] += 1
    print("\nMulti-source triangulation:", file=sys.stderr)
    for k in sorted(by_count.keys(), reverse=True):
        print(f"  {k} source(s): {by_count[k]} candidates", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
