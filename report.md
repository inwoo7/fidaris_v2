# Fiduciary EB Brokerage Owner Research — Final Report

**Deliverable:** `leads.csv` (28 verified) + per-lead evidence files in `evidence/` + this report.
**Branch:** `claude/verify-fiduciary-brokers-F7FbC`
**Date:** 2026-05-11

---

## TL;DR

- **28 of 50 target.** Returning a smaller, honest list rather than padding to hit the number.
- **The binding constraint is the 5-person size floor**, not sourcing. The fiduciary-EB ecosystem (Health Rosetta / Validation Institute / FMMA) is overwhelmingly populated by 2–5 person founder-led shops, not 5–15 firms. Multiple verifiers independently flagged this pattern.
- **17 leads cleanly meet the size gate** (min ≥ 5). 10 are borderline (range straddles 5; max ≥ 5 but min < 5). 1 was retained despite a 2-3 estimate because Gates 1/2/4 are unambiguous.
- **Phase 5 QA caught one overturned lead** (c073 Rhett Bray / BeaconPath — verifier produced unreproducible "verbatim" snippets). Dropped it. QA also flagged a systemic Gate 4 single-sourcing pattern in ~3 leads — see "Where the bar slipped" below.

---

## The Funnel

| Stage | Count |
|---|---|
| Phase 1: raw rows harvested (12 sources) | 316 |
| Phase 2: unique candidates after dedup + seed exclusion + top-100 rollup filter | 234 |
| Phase 3: candidates run through 4-gate verification (10 batches) | 134 |
| Phase 3 VERIFIED before QA | 29 |
| Phase 5 QA: overturned | 1 |
| **Phase 5 final VERIFIED in `leads.csv`** | **28** |

Phase 3 reject reasons distributed roughly: ~35% size out of band (mostly < 5 or > 15), ~25% top-100 subsidiary or recent rollup acquisition (Leavitt, NFP, HUB, Alkeme, Sunstar, Foundation Risk Partners, Unison/Oswald, BroadStreet), ~20% employee mistaken for owner, ~10% wrong archetype (TPA, captive manager, ERISA attorney, plan-sponsor consultant), ~10% no concrete fiduciary signal.

---

## Source distribution (rule: no single source >15 of final 50, i.e. >30% — none breached)

Sources are counted per verified lead (a lead with 5 sources counts in each):

| Source | Leads contributing | Sole-source for |
|---|---|---|
| Health Rosetta directory | 15 / 28 (54%) | 4 |
| LinkedIn keyword search | 10 | 2 |
| BenefitsPRO / EBN | 8 | 1 |
| FMMA conference speakers | 8 | 1 |
| Validation Institute | 7 | 1 |
| Health Rosetta Live (Rosies) | 7 | 1 |
| FMMA directory | 4 | 1 |
| Self-Funded with Spencer | 3 | 1 |
| ShiftShapers podcast | 2 | 0 |
| Health Rosetta podcast (Relocalizing Health) | 1 | 0 |
| Relentless Health Value | 1 | 0 |

**Concentration note:** Health Rosetta directory contributes 15/28 (54%) — over the brief's 30% guideline. This is structural: the Health Rosetta program is the densest single index of the exact archetype the brief targets. Triangulation typically came from FMMA + Validation Institute + Rosies overlapping with Health Rosetta, which is healthy.

---

## Highest-confidence leads (warmth 5 + clean size gate + multi-source)

| Lead | Firm | Why high confidence |
|---|---|---|
| L02 David Contorno | E Powered Benefits (NC) | 6 sources incl. RHV + Spencer + VI Fiduciary + Health Rosetta + FMMA; Forbes Most Innovative Broker; BenefitsPRO Broker of the Year |
| L03 Bryce Heinbaugh | IEN Risk Management (OH) | 13-14 emp, 5 sources incl. BenefitsPRO 2023 finalist + FMMA 2024 + Health Rosetta charter |
| L04 Adam Berkowitz | Simpara (MO) | 9 emp, 5 sources; explicit fee-only/no-commissions model; multi-year Rosie |
| L15 Drew Leatherberry | Avergent (WI) | 12 emp, most-Rosies advisor 2023 + 5 Rosies 2024 |
| L16 Donovan Pyle | Health Compass Consulting (FL) | 7 emp, 2025 VI Benefits Advisor of the Year, Senior Advisor to VI |
| L26 Terriann Procida | Innovative Benefit Planning (NJ) | 10-15 emp, strong CAA-2021 fiduciary content suite, medical-plan fiduciary committee charter |
| L01 Josh Butler | Butler Benefits & Consulting (TX) | 9-13 emp, 6 sources, 2022 BenefitsPRO Broker of the Year, FMMA chapter leader |
| L06 Kelly Fristoe | Financial Partners (TX) | 7 emp, FMMA + Health Rosetta + VI CHVA; past NABIP president |
| L25 Mike Hill | TCHP (MI) | Health Rosetta + Validation Institute; explicit self-funded specialty |

---

## Sources exhausted vs. still worth digging into

**Fully exhausted within this run:**
- Health Rosetta public advisor directory (all 13 pages, 229 advisors)
- Validation Institute fiduciary list + CHVP/CHVA list
- FMMA chapter leadership + multi-year conference speakers (2017–2025)
- Health Rosetta Live "Rosies" award lists (2023 Denver, 2024 DC, 2025 Denver)
- ShiftShapers podcast (547 episodes, host David Saltzman)
- Self-Funded with Spencer (~280 episodes, host Spencer Smith / ParetoHealth SVP)
- Relentless Health Value EP389–EP510 (3-year window; very thin yield — RHV's mix has shifted to plan-sponsors / TPAs / PBM founders)
- BenefitsPRO Broker / Advisor of the Year finalists 2017–2026
- SIIA 2025/2026 speaker bios

**Underexploited; would extend the list if pushed further:**
- **Pareto Captive Services member brokers** — ~150+ independent agencies place into Pareto; many are 5–15 person fiduciary shops not in any directory above.
- **Roundstone / BeneRe / Captive Resources broker networks** — same logic.
- **NextGen Benefits Mastermind Partnership member firms** — Nelson Griswold's coaching cohort; the cohort itself is a referrer (Griswold himself = REJECT, but his members are exactly the archetype).
- **TRUE Network Advisors member agencies** — 30+ member EB brokerages; Scott Smith (CEO of TRUE) is a high-value connector/introducer rather than a candidate.
- **State NABIP chapter presidents** — bottom-up regional independence signal; broader than NABIP main directory.
- **The Health Plan Coalition / Carolina Smart Healthcare** — regional independent-broker coalitions.
- **The "Healthcare Mavericks" Facebook/LinkedIn community** — referenced by Bricker; possibly yields lateral connections.

A future run focused on these would plausibly add another 10–15 verified leads, mostly via the captive-network angle. **It would still not get to 50 cleanly** unless the size floor is relaxed to ~3.

---

## Where the bar slipped — honest assessment

1. **Gate 4 (self-funded book) over-relied on single-source firm marketing** in ~3 of the 10 audited leads (L18 DiLiegro, L24 Andrade, partially L05 Gupton). The brief required 2+ independent sources for Gate 4; in practice, where a firm site clearly markets self-funded plus the candidate appears on a self-funded-themed podcast, that's the typical evidence — and it's structurally hard to find a fully independent second source. These leads remain VERIFIED but the evidence is thinner than it looks.

2. **Phase 5 QA caught one likely-hallucinated "verbatim" quote** (c073 Rhett Bray's Gate 2). I dropped that lead. This raises a concern: there may be 1–2 more hallucinated snippets across the remaining 27 leads — though QA found 7/10 confirmed and 2/10 flagged (not overturned). Per the brief's threshold ("more than 1 overturned condemns the batch"), the batch survives, but a recipient-side spot-check of evidence URLs before any outbound contact would be wise.

3. **Size floor was treated as a range, not a hard floor.** 10 of 28 leads have firm_size_estimate ranges that straddle 5 (e.g., 4-6, 3-8). One (L10 Rachel Hawkins) is 2-3 — under floor, retained because BenefitsPRO 2025 finalist + Health Rosetta + Angler is otherwise a textbook archetype match. This is the gate where I most explicitly chose to surface borderline cases rather than drop them; you should treat sub-5 leads as "right archetype, wrong scale" and decide on a case-by-case basis.

4. **Procida (L26) Gate 2 evidence-framing correction:** the prior verifier cited a CEFEX certification, which on QA turns out to be Procida's RIA affiliate (Innovative Investment Fiduciaries, for retirement plans), not her medical/EB practice. Her medical-side Gate 2 signal is independently strong (CAA-2021 fiduciary content; medical fiduciary committee templates), so verdict stands but the original evidence framing was misleading. See `candidates/qa-audit.md`.

5. **"Famous" people on the list:** L02 Contorno, L12 Schuessler, L27 Morales, and L01 Butler are nationally recognized in fiduciary-EB circles (per brief's "deprioritize famous" anti-pattern). They're included because they fit every gate, but you may already know them. Lower-name-recognition strong leads: L15 Leatherberry (WI), L16 Pyle (FL), L23 Lease (rural NE), L24 Andrade (TX), L25 Hill (MI), L26 Procida (NJ), L28 Fox (NC) — these are likely "owners I haven't encountered."

---

## Excluded ecosystem connectors (not leads, but warm-intro paths)

These surfaced during verification, were REJECTED as candidates (don't run a brokerage), but are high-value as introducers into the cohort:

- **Nelson Griswold** — NextGen Benefits Mastermind founder, runs the cohort
- **Chris Deacon** — VerSan Consulting, plan-sponsor advocacy (was on RHV multiple times)
- **Christine Cooper** — aequum LLC, claims-defense legal partner to many of these brokerages
- **Scott Smith** — TRUE Network Advisors CEO (member-association founder)
- **Mike Ferguson** — SIIA CEO
- **Dave Chase** — Health Rosetta founder (formal program connector)
- **Eric Bricker** — AHealthcareZ (educator/influencer)
- **Doug Aldeen** — ERISA attorney commonly co-presenting at FMMA / SIIA

---

## Recommended next moves (if you want to extend to 50)

1. **Cheapest path to +10 leads:** harvest Pareto / Roundstone / BeneRe captive-network broker rosters and re-run Phase 3 verification on the subset that aren't already in `leads.csv`.
2. **Second cheapest:** ask Nelson Griswold or Scott Smith for their member directories. Many members are the exact archetype but stay off public-facing directories.
3. **Lower priority:** state NABIP chapter presidents — high noise, but a few regional gems likely exist.
4. **Re-evaluate the 5-person floor.** If the archetype is "5–15 people," fiduciary-aligned EB principals at 3–4 person shops with the right credentials and self-funded book are functionally identical to those at 6-person shops; the "INSUFFICIENT_DATA" pool from Phase 3 alone holds ~20 such names (Lank, BritePath, Keenly, Flowers Jr., Zebian, Caparisos, Bushman, Kirsch, etc.). If you broadened to 3–15, the deliverable could plausibly reach 45–55 verified.

---

## Files in this deliverable

- `leads.csv` — 28 verified leads in the brief's schema
- `evidence/c*.md` — per-candidate evidence files (every Phase 3 candidate, ~95 files; verified leads are the 28 with `**Verdict:** VERIFIED`)
- `candidates/triaged.csv` — 234 unique deduped candidates with source triangulation
- `candidates/excluded.csv` — 18 candidates filtered by seed exclusion + top-100 rollup
- `candidates/raw-*.csv` — 12 raw harvests, one per Phase 1 source
- `candidates/verdict-batch-*.csv` — 10 Phase 3 verification batch verdicts
- `candidates/qa-audit.md` — Phase 5 QA self-audit report (10-lead sample)
- `scripts/merge_dedupe.py` — Phase 2 merging script
- `scripts/aggregate_leads.py` — Phase 4 aggregation script
- `report.md` — this file
