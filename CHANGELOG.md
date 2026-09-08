# Changelog

Notable changes to the rubric and the harness. The rubric versions (v1-v3) are
the substance of the project; the harness changes after that are tooling.

## Rubric iterations

### v1 - rubric as first written
Exact-match agreement with human labels: **46%** (23/50). "fit" precision 43%,
recall 93%, F1 0.59.

Target role types were product management, AI / ML engineering, any function at a
well-known tech company, and consulting. Undergraduate degree gate. A pay floor
is in the written rubric but the benchmark has no salary field, so it is not
scored.

Reading the per-row disagreements, the errors were one-directional: v1 marked
almost any AI / ML / data role at a recognizable company `fit`, and every one of
those was a human `no`. A stated-vs-revealed preference gap: the written criteria
claimed more breadth than the labels ever used.

### v2 - target role types narrowed to revealed preference
Exact-match agreement: **74%** (37/50). "fit" precision 62%, recall 93%, F1 0.74.

- Data / analytics / research titles -> `no` (not a target for this persona).
- Product management title -> `fit`.
- Operations / supply chain title -> `fit`.
- Consulting firm -> `fit`.
- AI / ML engineering title -> `maybe` (in scope in principle, gated by a coding
  screen the persona does not clear this cycle).
- Degree gate unchanged.

### v3 - company-tier factor
Exact-match agreement: **82%** (41/50). "fit" precision 92%, recall 86%, F1 0.89.

v2's residual errors were company-desirability calls. v3 adds one rule: an
on-target product or operations `fit` at a company on a hand-built lower-profile
list is downgraded to `maybe`. The list was built after seeing these 50 rows, so
on a fresh set it needs re-checking. That is the regression-test use case.

The remaining ~18% disagreement is mostly "would the persona actually want this
specific employer", which a keyword scorer cannot encode. Next version replaces
the rule-based scorer with an LLM-as-judge that takes the criteria as a prompt
and is evaluated against this same labeled set.

## Harness

Changes to the tooling around the rubric, newest first.

- `--check` mode: `python eval.py --check` exits non-zero if v3 agreement drops
  below `--min-agreement` (default 0.78). A regression gate for rubric edits.
- `eval.py` writes `results/summary.md` and `results/disagreements.md` on each
  run, and both are committed, so a rubric change is a reviewable diff.
- Macro-averaged F1 across all three classes added to the summary table
  (v1 0.36, v2 0.59, v3 0.79). The fit-only F1 hides that v1 never predicts
  `maybe`; the macro number does not.
- Scoring and metrics factored into importable functions (`load_rows`, `score`,
  `prf`).
- `unittest` suite (`test_eval.py`) locks the v1 / v2 / v3 baseline numbers and
  covers the degree gate, the data-title and AI-engineering rules, v3's
  lower-profile downgrade, and determinism.
