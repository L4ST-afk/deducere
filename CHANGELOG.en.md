# Changelog

[中文](CHANGELOG.md) · English

## Unreleased (2026-11-27) · Branch protection: add quality-gate aggregate

- **Problem**: the repo had no branch protection at all; anyone, including the local pipeline, could push straight to main.
- **Change**: a `quality-gate` aggregate job at the end of `selftest.yml` (`needs: [checks, docs]`, `if: always()`): both the offline gate and the docs gate must succeed; failure, cancellation, or skip turns it red.
- **Why not pin the matrix jobs**: names like `离线闸 · py3.11` change with the matrix, so a required check pinned to them silently expires; the aggregate name is stable.
- **Alongside**: main now requires `quality-gate`, `strict: true`, `enforce_admins: true` — everything goes through PRs from here.
- **Untouched**: criteria (J1–J30), scripts, tests, docs.

## 1.1.0 (2026-11-26) · Compound-symptom splitting and stronger feedback loops

- Compound requests are split first: pure styling, new features, generic performance work and defect diagnosis take separate paths; each symptom gets its own red/green chain and rollback point.
- The red/green gate now checks fixture health, treating import, name, attribute and syntax errors as loop failures by default. Service retests check instance freshness, while UI evidence distinguishes truth, structure and presentation.
- The criterion table now carries 30 entries (J1–J30), with 27 business regressions. Performance measurement and truth-slice ownership remain in the candidate pool rather than claiming promotion.
- The naming, visual-language and performance-measurement volumes are public; the local-use declaration and field notes are not shipped.

## 1.0.1 (2026-11-25) · Cover easter egg gains the three pairings

- The README easter-egg section grows from "four birds, four stones, trade beads" to three pairings: in time (Peruvian Moche hammered-gold plaques ↔ twentieth-century African trade beads), in space (Peru ↔ Yueqing across the globe; South America ↔ West Africa with interlocking coastlines), in meaning (*Dui Niao* answers signs with a bird's name ↔ this skill answers symptoms with a root cause).
- One added note on provenance and ethics: the beads were made in Europe (Venice, Bohemia, the Netherlands) and carried into Africa by ocean trade — also evidence of the triangular trade, kept here only as corroborating imagery.
- The 29 criteria, scripts and self-check: untouched; the visual canon stays an internal volume, not shipped.

## 1.0.0 (2026-11-25) · First public release

- Released with the independent "Four Questions, Three Ledgers" construction: four questions (discern / trace / verify / clean) and three ledgers (process / result / evidence).
- Core discipline: a green process ledger never settles the result ledger; "resolved" requires evidence from a later period.
- 29 criteria (J1–J29) in three-line form (question / violation / symptom), with a single source of truth in `references/判据表.md`.
- Executable scripts: `verify_red_green.py` (red/green hard gate), `check_clean.py` (clean-trace check), `human-loop.template.sh` (human-in-the-loop fallback).
- 24 unit tests plus an offline self-check (`scripts/selftest.py`), zero third-party dependencies.
- Cover art draws on the four-question folk song "Dui Niao"; the visual canon is an internal volume, not shipped with the public build.

### Release redaction

- Internal project cross-references, paths, review records and bare reference numbers were removed or rewritten as self-contained statements.
- The local-use declaration and field notes are not part of the public release.
- See LICENSE / NOTICE for licensing and attribution.
