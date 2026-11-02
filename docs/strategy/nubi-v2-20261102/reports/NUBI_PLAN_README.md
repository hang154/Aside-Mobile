# NUBI Strategy v2.0 Reproduction Guide

- Release date: 2026-11-02 (Asia/Seoul).
- Source: `scripts/source/NUBI_MASTER_SOURCE_20261102.md`; original legacy input: `붙여넣은 텍스트(1).txt`.
- Output: `artifacts/*.md`; reports: `reports/*`; bundled ZIP at root.
- Parameters: 23 slides, 18 VC questions, finance per calendar-month MAU, action variable costs per verified attempt; no random seed.
- Dedupe: distinct stable IDs `S01-S23`, `Q01-Q18`; preserve all authored prose without automatic deduplication.
- Run: `python3 scripts/generate_nubi_strategy.py`.
- Validate existing outputs without modifications: `python3 scripts/generate_nubi_strategy.py --validate-only`.
- Compare legacy/current: `reports/old_vs_new_diff.csv` (exact line-level diff), `reports/NUBI_PLAN_CHANGELOG.md` (semantic comparison).
- Hashes: `reports/sha256_report.json`; validation results: `reports/reproduction_check.csv`.
- Financial examples are **hypotheses**, not live users or ad revenue.
- Git status: `/mnt/data` is not a Git checkout, so local git commit is unavailable. Connected private GitHub repository was read to verify 0.6.13; this script does not push or change remote GitHub files.
- Source provenance: prior user-provided deck and conversation plus private GitHub code and public citations listed in the master.
