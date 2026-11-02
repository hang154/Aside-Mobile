# NUBI Strategy v2.0 — Repository Import (2026-11-02)

This directory is a **self-contained, additive** import of the user-provided `NUBI_STRATEGY_V2_REPRODUCIBLE(1).zip` into the existing `Aside-Mobile-Backup` private repository. Application sources and the existing release branches are intentionally unchanged.

## Contents

- `artifacts/`: investor executive summary, 23-slide *script*, VC Q&A (18), and the business master plan.
- `scripts/source/`: authoritative business-master Markdown; `scripts/generate_nubi_strategy.py` rebuilds artifacts, diff, and hash reports.
- `붙여넣은 텍스트(1).txt`: unmodified legacy investor draft embedded in the uploaded archive. **It is not a verbatim transcript of all user prompts.**
- `prompts/NUBI_USER_PROMPTS_20261031_20261102.md`: direct quotations and explicitly flagged excerpts of NUBI-related user requirements in this dialogue, plus a separate index of earlier requests whose full verbatim wording was not available.
- `reports/`: release hashes, reproduction check, legacy-vs-current diff, and change log.

## One-command verification

From this directory:

```bash
python3 scripts/generate_nubi_strategy.py --validate-only
```

To rebuild: `python3 scripts/generate_nubi_strategy.py` (writes a reproducible ZIP within this directory; the uploaded ZIP itself is not committed as a binary).

## Provenance and scope

The uploaded archive was checked with `ZipFile.testzip()` and all 12 members were extracted without path traversal. The original generator's validation passed (23 slide IDs, 18 VC questions, 3 financial scenarios). Source text and generated reports were preserved as provided; this import did not silently revise the investment claims.

The strategy material is **a plan, not a product release**. The checked private GitHub `0.6.13` verification record says real school authentication, GPT/Claude/Gemini integration, Drive upload, real assignment submission and bookings/checkout remain unverified or incomplete. Commit `244860b4cc14ce2400df246a62f216e0fff533d3` exists but should not be equated with the main branch head without verifying ancestry. This strategy import does not merge that implementation commit.

No account credentials, cookies, user documents, or APKs are included in this strategy import. For investor releases, review raw prompt files to decide what may be shared outside the private repo.

## Stable paths

- This README is the import's entry point.
- Do **not** replace current Android implementation with this research package.
- File integrity is checked using the original SHA-256 manifest in `reports/sha256_report.json`.

## Version note

The generator's original `reports/NUBI_PLAN_README.md` says it was created outside a Git checkout. That was accurate **when the ZIP was built**; the present README documents the later GitHub import. Keep the original report intact for byte-identical reproduction.
