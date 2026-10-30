# Understanding-layer prototype (2026-10-30)

**Status: rapid prototype.** Zach asked to see "how far DataGuide can get with the recovered vision", building it as a rapid prototype and working around ambiguity rather than blocking on it. The source is the Google Doc *Data Guide — Recovered Vision, EDA Philosophy & Claude Handoff — 2026-10-27*. That doc describes itself as a working synthesis, not an approved specification. Everything below is provisional unless Zach accepts it.

- **Built by** Claude (AEC lane).
- **Purpose review** by Kate (ChatGPT).
- **Intent recorded before code** in `.aec/records.jsonl` (the AEC pilot).

## What it adds

`guide understand FILE [--annotations guide.yml]` writes three files:
- `guide-profile.json`, a versioned artifact (`data-guide/understanding@0.1`) with a dataset fingerprint;
- `guide-report.md`;
- `guide-report.html`, self-contained, with the charts embedded.

`guide compare BEFORE.json AFTER.json` shows before/after deltas. `guide demo` writes a synthetic table with planted problems and runs the guide on it.

| Recovered vision | What the prototype does | Status |
|---|---|---|
| A. Separate observations, interpretations, hypotheses, actions | Every finding is typed and names its generator (`rule` or `human`). Confidence means different things per kind: `measured`, `untested`, `stated` | built |
| B. Inferred types are not domain facts | Semantic types carry confidence, reasons and alternatives, and are marked `inferred`. Annotations override them as `human`, the inference is kept, and a disagreement between the two raises a question | built |
| C. Question and semantics govern analysis; no combinatorial dashboards | Pair screening is selective: target pairs first, within a budget. Excluded columns are listed with reasons. Only the strongest non-negligible pairs are shown. Wide tables organised by period are detected and their per-column noise is summarised | built (narrow) |
| D. Re-profile and compare | `guide compare` reports changes by column and findings resolved or new. It warns when missing values have been filled, so filled values aren't read as observed (Kate's fixture) | built |
| E. Machine-readable artifact is the interface | `guide-profile.json`, a proposed serialization of the approved `ProfilingResult`, which now has an optional `understanding` field. Markdown and HTML are derived from it only | built (provisional) |
| F. Tests for metric accuracy, type routing, degradation, reproducibility, purpose | 59 new tests, each check with a violating fixture and a clean decoy, plus byte-identical determinism, a test that runs without matplotlib, and regressions for every defect the independent technical review found | built |
| Assumptions and data-generating process | A register of what the table can't tell: row unit, generating process, missingness mechanism, candidate keys, shape. Unknowns become open questions, never guesses | built |
| Usefulness | Needs a declared question, decision or target. Without one the report says *decision-specific usefulness: unassessed*, and exploratory findings are still reported | built |
| Human vs AI interpretation | Human interpretations come from `guide.yml`. There is no AI-generated text; `ProfilingResult.annotations` stays the extension point for that | built |

## Acceptance loop (Kate's test, on an unfamiliar dataset)

The dataset is World Bank total fertility rates, 219 rows × 58 columns, bundled with statsmodels. Reproduce it with `python docs/prototype/acceptance_fertility.py OUT`.

1. **Initial profile.** The guide reports:
   - a wide table: 54 columns named 1960–2013, one per year;
   - missingness rising from 11% in 1960 to 100% in 2012–13;
   - two constant indicator columns;
   - five labels in `Country Name` that read like groupings: "OECD members", "Sub-Saharan Africa (IFC classification)" and others.

   It asks whether the late years are unpublished or uncollected, and which rows are countries and which are groupings.
2. **Concern.** The table isn't one row per country. Some rows are aggregates of other rows. Averaging across all rows would double-count, and nothing in the raw table says so.
3. **Recorded transformation.**
   - Reshape to long: one row per country-or-group and year.
   - Drop the two constants.
   - Impute nothing.
   - Annotate the row unit and meanings, and add a human interpretation that groupings must be excluded before averaging.
4. **Re-profile and compare.** 16 findings no longer fire, all tied to the wide shape. New ones appear:
   - missingness in `fertility_rate` varies with `year` (100% in 2012, 6% in 2007; chi-square, Bonferroni-adjusted, Cramér's V 0.51), so the data is unlikely to be missing completely at random;
   - a negative association between fertility and year, pooled across countries.
5. **Still unknown:**
   - which of the 219 labels are groupings (the heuristic found 5, and there are likely more);
   - why the late years are empty;
   - how the World Bank produced the series.

   An analyst should list the groupings explicitly and look at trends within each country before pooling.

**Kate's success criterion:** "Can the analyst understand something consequential about the dataset that the initial table did not make obvious, without Data Guide pretending to know more than it does?" For this dataset, yes. The aggregate rows and the year-dependent missingness are both consequential, and neither is visible in the raw table. The guide stated each as a measurement, hypothesis or question, not as fact.

This loop was used to *develop* the rules: the wide-table, aggregate-label and missingness-by-group rules came from running it. So it is a development fixture, not a held-out evaluation.

## Independent technical review

A fresh agent that hadn't seen the build reviewed the PR. It confirmed the core statistics against scipy and numpy (Spearman, η, bias-corrected Cramér's V, quantiles, skew, histograms), checked determinism across hash seeds, and checked HTML escaping. It found 6 blocking and 12 non-blocking defects.

The most serious: the first missingness-by-group rule fired on purely random missingness in 20 of 20 trials. It is now a chi-square test with a minimum group size, Bonferroni adjustment and an effect-size floor, and it is worded "varies with". The other fixes:
- timestamps with mixed UTC offsets no longer crash the build, and nor do infinite values or non-string, duplicate or nested column names;
- `compare` now detects a zero fill even when the column already had zeros, and keeps each finding's generator;
- small-scale statistics are rounded to significant figures;
- wording is corrected for left skew and for the wide-table finding;
- single-row tables are handled;
- numeric column names can be annotated;
- `$` in chart labels and Markdown escaping are fixed;
- rule readings are labelled `heuristic` rather than an unmeasured "medium".

Each fix has a regression test. Runtime on 100k rows × 100 columns is about 34 s.

## Known limits

- The rules are heuristics, and English-language name and label heuristics in places (aggregates, sentinels, test values). They will miss things and sometimes misfire. Every rule-generated hypothesis is labelled as one.
- Associations are pooled. There are no within-group or time-series checks yet (for example, autocorrelation or seasonality).
- No quality score. No weights were ever chosen, so none were invented.
- The legacy `DataProfiler` (`src/data_profiler.py`) is untouched apart from a pandas 2 fix (`infer_datetime_format` removed). The approved April plan to migrate it, not rewrite it, still stands; this prototype doesn't replace it.
- `AGENTS.md` and `CHARTER.md` describe other projects (Predictions/STARS, Cognitive-Scaffolding). Don't treat them as Data Guide's operating rules until they are reconciled. This is recorded in `.aec/records.jsonl`.
