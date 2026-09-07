# Internship-Fit Eval

A small evaluation harness for an LLM-style classifier: a rubric that scores
internship postings **fit / maybe / no** for one candidate persona. The rubric
started as a few paragraphs of written criteria inside a personal job-search
assistant. This project measures whether it actually matches human judgment, and
uses the gap to fix it.

The classifier is not the interesting part. The eval is: a labeled benchmark, a
scorer, an agreement metric, a look at *where* the disagreements fall, and three
tuning iterations that move the number.

## Result

| version | what changed | exact-match agreement | "fit" precision | "fit" recall | "fit" F1 |
|---|---|---|---|---|---|
| v1 | rubric as first written | **46%** | 43% | 93% | 0.59 |
| v2 | target role types narrowed to match revealed preference | **74%** | 62% | 93% | 0.74 |
| v3 | + company-tier factor | **82%** | 92% | 86% | 0.89 |

50 hand-labeled postings. Metrics are computed on all three classes for exact
match, and on the `fit` class for precision / recall / F1 (the class a job filter
most needs to get right).

## What the eval caught

v1 agreed only 46% of the time. Reading the per-row disagreements, the errors
clustered in one direction: v1 marked almost any AI / ML / data role at a
recognizable company as `fit`, and every one of those was a human `no`.

That is a **stated-vs-revealed preference gap**. The written criteria listed "AI
engineering" and "big tech, any function" as targets. The actual labels only ever
say `fit` to product management, operations, and consulting. v2 rewrites the
target role types to match what the labels actually do. v3 then handles the
second-order pattern: an on-target role still scores lower at a low-profile
employer than at a strong-brand one.

The residual ~18% disagreement at v3 is mostly company-desirability judgment
(would the persona actually want this specific employer), which a keyword scorer
structurally cannot capture. See **Limitations**.

## Run it

```
python eval.py
```

No dependencies. Standard library only, Python 3.8+. Prints the summary table,
plus confusion matrices and full disagreement lists for v1 and v3.

## Repo layout

```
eval.py           the three rubric versions + the scoring / metrics harness
criteria.md       the rubric, all three versions, in prose
data/postings.csv 50 postings: company, role, locations, degrees, category, label, url
```

## Data notes

- Postings are real Summer 2027 internship listings collected from public job
  boards and a public aggregated tracker in September 2026. Only fields needed for
  scoring were kept.
- Labels (`fit` / `maybe` / `no`) are one person's judgments for one persona:
  undergraduate, targeting product management / consulting / operations. They are
  preferences, not ground truth about the roles.
- The set was sampled for variety on purpose: clear fits, clear rejects,
  borderline cases, and degree-restricted roles to exercise the eligibility gate.
  Class balance is 14 fit / 6 maybe / 30 no.

## Limitations

- **Single labeler.** No inter-rater agreement; the "ground truth" is one
  person's calls. A second labeler would let you measure label noise.
- **Small set.** 50 examples, 14 in the `fit` class. The metrics have wide
  confidence intervals; treat 46 -> 82 as a direction, not a precise delta.
- **Keyword scorer has a ceiling.** Company desirability and nuance in a title
  ("AI Intern" at an insurance company vs. a lab) are hard to encode as rules.
  The natural next version replaces the rule-based scorer with an LLM-as-judge
  that takes the criteria as a prompt, and is itself evaluated against this same
  labeled set for judge bias and agreement.
- **Fit to the set.** v3's company-tier list was built after seeing these 50
  rows. On a fresh set it would need re-checking; that is the regression-test
  use case.

## License

MIT
