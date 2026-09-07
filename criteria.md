# The fit rubric

The "classifier" being evaluated is a written rubric that sorts an internship
posting into **fit / maybe / no** for one candidate persona: an undergraduate
targeting product management, consulting, and operations roles for a summer
internship.

`eval.py` encodes three versions. The point of the project is to watch the
version change as the benchmark exposes where each one is wrong.

## Inputs available per posting

`company`, `role` (title), `locations`, `degrees` (degree levels the posting
accepts), `category` (Product or AI/ML/Data, from the source feed).

## v1 - the rubric as first written

1. **Degree gate.** If the posting lists degree levels and none is a bachelor's,
   return `no`.
2. **Target role type -> `fit`** if the title matches any of: product management,
   AI / ML engineering, or the company is a well-known tech company (any function),
   or the company is a consulting firm.
3. Otherwise, a data / analytics / research title -> `maybe`.
4. Otherwise -> `no`.

A pay floor is part of the written rubric ("exclude anything below a set hourly
rate"), but the benchmark carries no salary data, so it is not applied.

## v2 - rewritten after reading v1's mistakes

v1 agreed with the human labels only 46% of the time, and the errors were not
random (see the README). v2 narrows the target:

1. **Degree gate** (unchanged).
2. **Data / analytics / research title -> `no`.** Not a target role type for this
   persona, regardless of company.
3. **Product management title -> `fit`.**
4. **Operations / supply chain title -> `fit`.**
5. **Consulting firm -> `fit`.**
6. **AI / ML engineering title -> `maybe`.** In scope in principle, but gated by a
   coding screen the persona does not clear this cycle.
7. Otherwise -> `no`.

## v3 - v2 plus a company-tier factor

The remaining v2 errors were company-desirability calls: the persona would take a
PM role at a strong-brand company but only "maybe" the same role at a low-profile
industrial or insurance employer.

- Same as v2, except: an on-target **product / operations** `fit` at a company on
  the lower-profile list is downgraded to `maybe`.

The lower-profile list in `eval.py` is a hand-built heuristic, not a data-driven
tier model. That is deliberate: encoding "is this a company the persona wants" as
keywords has a ceiling, which is the main limitation discussed in the README.
