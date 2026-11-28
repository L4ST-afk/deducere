# Changelog

[中文](CHANGELOG.md) · English

## Unreleased (2026-11-28) · "鸴" traced: the simplified form of 鷽, the song's "long-tailed bird"

> Basis: evidence supplied by the user on 2026-11-28, re-checked by this seat with two searches. Honesty gap #7 is withdrawn as "unverified" and re-recorded as "verified, with one link still open".

- **Verified**: 鸴 is the simplified form of 鷽 (xué); Erya: "鷽, the mountain magpie", Guo Pu: "like a magpie but patterned, long-tailed, red bill and feet"; the song's "long-tailed bird" is the red-billed blue magpie, anciently called the mountain magpie / 鷽.
- **One link still open**: the dictionaries record only the bird's appearance; "the red-billed blue magpie was anciently called 鷽" is matched by description, with no classical text found that names it directly, nor any Yueqing gazetteer.
- **naming.md**: §8's 鸴闸 row now names the song bird; its image is inverted from the Shuowen "bird that knows what is to come" — the gate forbids predicting the outcome; §6 gains four sources.

## Unreleased (2026-11-28) · The four hard gates take the song's birds as names: Kingfisher / Pheasant / Dove / Xu

> Basis: user sign-off on 2026-11-28. Provenance and the honesty gap: `references/naming.md` §8.

- **SKILL.md §7**: symptom exit gate = **翠闸 (Kingfisher)**, red/green gate = **雉闸 (Pheasant)**, clean-trace gate = **鸽闸 (Dove)**, delayed re-verification gate = **鸴闸 (Xu)**. The bird names are codenames for the gates, not fix clauses; "bird = the riddle's answer" is unchanged.
- **Scripts**: the first docstring line of `verify_red_green.py` and `check_clean.py` carries the gate name; file names and output tokens (`PASS-RED` etc.) are untouched.
- **naming.md**: new §8 mapping table; honesty gap #7 (the link between 「鸴」 and the song's 「长尾巴丁」, its meaning and reading, are unverified).

## Unreleased (2026-11-28) · The red/green gate reads out the actual failure line for you

> Basis: field debugging of a sibling criteria set's entry pipeline (2026-11-28; the three reds behind §2.399–2.403).

- **Gap**: on "symptom mismatch" `verify_red_green.py` said only that the regex was not hit, not what actually failed; the person locking the red had to rerun raw and dig through long output. Three reds took three re-locks (probe tripped the duplicate-title guard / `--match` named a neighbouring failure / wrapper mapped red and green backwards) — the gate caught every one, but each cost an extra round trip.
- **Red/green gate**: on mismatch it now also prints the command's **actual last line** and names the next step ("do not edit `--match` to fit the output; fix the probe"); new regression `test_28`.
- **Feedback-loops volume**: adds "four rules for a self-built red" (read the failure line before locking / probe inputs must clear unrelated guards / wrapper mapping and stderr / what the red really is for a missing entry point) and "time each gate before batching" (batches that exceed the foreground wait get stopped mid-way and leave a half-written tree).
- **Corruption signals**: adds "re-locking fails, so edit `--match` to fit the output".

## Unreleased (2026-11-27) · The evidence gate gains a local fallback

> Basis: voyage card github-mirror-skills-refit-p1 — structural-analogy survey and graceful-degradation refit (2026-11-27).

- **Gap**: the evidence ledger requires every conclusion to trace back to a command and an exit code, and its full form relies on an external review channel. With no channel there were only two options: ship nothing, or write "reviewed" over "not reviewed" — the second is a false ledger.
- **New `scripts/evidence_gate.py`**: probes the executable named by `DEDUCERE_REVIEW_CHANNEL`. Present → reports `external: true` and hands over to the channel. Absent → runs the three local gates only (residue, red-green, syntax smoke) and records "enhancement not enabled: missing external review channel".
- **One set of truth**: the local gates emit only command, exit code and last summary line, and never produce a conclusion that only external review can reach.
- **Three outcomes reported apart**: `pass` / `findings` / `incomplete` with exit codes 0 / 1 / 2 — "could not run" never impersonates "found something".
- **Repository-root resolution**: `check_clean.py` wants a Git repository root and reports `[USAGE ERROR]` for a subdirectory. `resolve_repo()` walks up with `git rev-parse --show-toplevel`; when there is no root it records "could not run".
- **What is lost**: whether the symptom is the one the user reported (locally only the command's redness is proven), whether the fix sits where the bad value was first produced (J18 needs a human on the causal chain), and whether an interval re-check holds (J24 needs time).

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
