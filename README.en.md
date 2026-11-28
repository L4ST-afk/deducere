# Deducere (对鸟) · Evidence-Driven Root-Cause Debugging

[中文正本 (canonical)](README.md) · English

<!-- cover slot: once `docs/cover.jpg` lands, insert
     <img src="docs/cover.jpg" alt="Deducere — four separated hammered-gold bird plaques on deep forest-green felt, facing antiphonally, with emerald, white diamond, ruby, and sapphire eye stones and 20th-century trade beads" width="720">
     ⛔ No placeholder link while the image is missing. -->

> Visual canon (bird–stone mapping, goldwork and bead origins, and the three antitheses of time / space / meaning): [references/visual-language.md](references/visual-language.md) (Chinese canonical).

> *Mountain song of Yueqing, four birds singing in antiphonal reply.*
> *One asks which bird flies past in verdant green; the other answers where that plumage grows.*
> *One asks which bird rings like a striking brass bell; the other answers where the mechanism sounds.*
> *Until doubt is broken, the crimson eye burns like a beacon; one question, one proof, tracking the trace to its source.*
> *Never alter a single line on guesswork — first force the red, then turn it green, severing the fault where the bad value is born.*

**Deducere** is a disciplined debugging and root-cause isolation skill for AI coding agents. It enforces reproducible red-green verification, ranked falsifiable hypotheses, single-variable instrumentation, and post-fix workspace hygiene — separating *educated guessing* from *proven root-cause repair*.

The Chinese name **对鸟** follows the national intangible cultural heritage antiphonal folk song from Yueqing, Wenzhou, where every question demands an exact, rhythm-locked answer before the song may proceed; the Latin name **Deducere** means to trace down and deduce. Naming and canonical pronunciation are fixed in [references/naming.md](references/naming.md).

---

## Four Questions, Three Ledgers (core construction)

Debugging is not a six-step pipeline. It is four questions you can re-enter, plus three ledgers that never substitute for one another. The questions have no fixed order; one one-way rule binds them: **a green process ledger never settles the result ledger**.

| Question | Cover bird | What it answers | Exit (machine-checkable) | Exit (human, with evidence grade) |
|---|---|---|---|---|
| Discern | Green dove · emerald | Does this red assert the exact symptom? | `verify_red_green.py --expect red` rc=0 | asserts the user's exact symptom, not "no crash" [L1] |
| Trace | White dove · diamond | Which line holds the chain, where was the bad value born? | — | ≥2 falsifiable hypotheses, `file:line` opened this session, trivial causes first [L0] |
| Verify | Pheasant · ruby | Same command red-then-green? | `--expect green` rc=0 on the same command | seam runs the real trigger chain, fix at source [L1] |
| Clean | Blue magpie · sapphire | Probes removed, source fixed, relapse prevented? | `check_clean.py` rc=0 | six-item checklist + eight-part report + result ledger pending [L0] |

**Three ledgers**: process (judgeable now, machine + this session), result (judgeable only later, by a person or a later re-run), evidence (graded L0/L1/L2 with a rereadable path). All four questions green means process compliance only; with no later-stage data the result ledger is "insufficient evidence" — never write "resolved".

> **Single carrier of criteria**: all 30 criteria (question / violation / symptom), grouped by the four questions as J1–J30, live in [references/判据表.md](references/判据表.md); SKILL.md and expansion volumes cite IDs only.

## Self-Check & Daily Commands

Offline regression (zero dependencies, no network):

```bash
python3 scripts/selftest.py                      # Syntax smoke check; expect PASS, exit 0
python3 -m unittest discover -s tests -q         # Business regression for both gates; expect OK, exit 0
```

Debugging and pre-delivery gates:

```bash
# 1. Lock in the failure before touching code (must exit non-zero and match symptom regex)
python3 scripts/verify_red_green.py --expect red --cmd "<repro-cmd>" --match "<error-regex>"

# 2. Prove the fix after patching (same command must exit 0)
python3 scripts/verify_red_green.py --expect green --cmd "<repro-cmd>"

# 3. Audit working tree before delivery (exits 1 if any [DEBUG-*] probe remains)
python3 scripts/check_clean.py --repo .
```

## Layout

```text
对鸟Deducere/
├── SKILL.md                    # Six-phase rule book, hypothesis ranking, stop-loss thresholds
├── references/
│   ├── 判据表.md               # 30 criteria (question / violation / symptom; Chinese canonical)
│   ├── naming.md               # Naming, canonical pronunciation, rejected candidates
│   ├── feedback-loops.md       # Feedback-loop seams, tightening, nondeterministic bugs
│   ├── hypothesis-methods.md   # Sibling-skill comparison, boundary bisection, panel review
│   ├── anti-patterns.md        # Root-fix anti-patterns, case-vs-general, prevention options
│   ├── reporting-and-handoff.md # Report template, clean-sweep checklist, handoff facts
│   ├── provenance.md           # Independent-implementation statement, construction sources
│   ├── visual-language.md      # Visual canon: bird–stone mapping, goldwork/bead origins, three antitheses
│   └── pending-thresholds.md   # Pending calibration numbers (P pool)
├── scripts/
│   ├── verify_red_green.py     # Red-before / green-after falsification gate
│   ├── check_clean.py          # Post-fix hygiene scanner for [DEBUG-*] leftovers
│   ├── selftest.py             # Syntax-level offline smoke check
│   └── human-loop.template.sh  # Structured human-in-the-loop template (authored in this skill)
└── tests/
│   └── test_deducere.py        # 28 business regression cases for both gates
```

## Cover Motifs (Design Easter Eggs)

<details>
<summary>🎨 Cover inscription and four-stone metaphor (click to expand)</summary>

The cover draws on the Yueqing antiphonal folk song *Dui Niao*: four hammered-gold bird plaques face one another, each set with an eye stone, standing for four core debugging disciplines. The Chinese inscription rhymes in the eng/ing class (míng / míng / chéng / méng); the rendering below keeps the meaning, not the meter.

> Four birds face each other, question answering question.
> Which bird flies past in green on green? — Discern the signs first, name the cause.
> Which bird rings a brass bell? — Trace the chain down, the origin stands clear.
> Which bird wears red between green? — Red before green: the check proves out.
> Which bird dyes its lips rouge? — Wipe every trace clean; no relapse shall bud.

| Gold bird | Eye stone | Inscription line | Question metaphor |
|---|---|---|---|
| Green dove (青翠) | Emerald | Discern the signs first, name the cause | Discern: assert the exact symptom, no shadow-chasing |
| White dove (白鸽) | White diamond | Trace the chain down, origin clear | Trace: falsifiable candidates, one variable per run |
| Ring-necked pheasant (雉鸡) | Ruby | Red before green, check proves out | Verify: same command red first, green only after the fix |
| Red-billed blue magpie (长尾巴丁) | Sapphire | Wipe traces clean, no relapse | Clean: repair where the bad value is born, remove every probe |

Loose between the plaques lie trade beads — agate/chalcedony stones and millefiori glass, never strung — standing for cross-system call chains and data clues; follow the beads along the thread to the true cause. Full visual canon: [references/visual-language.md](references/visual-language.md) (Chinese canonical).
</details>

## License & Internal-Use Note

This skill is an independent implementation — not derived from, translated from, or a rewrite of any upstream work. Its construction, criteria, scripts, narrative and body text are authored in this library, with no MIT or other upstream license obligations. See [provenance.md](references/provenance.md).

The public distribution does not include the local-use declaration or field notes.
