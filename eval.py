"""
eval.py - deterministic evaluation of an internship-fit scoring rubric.

A job-fit "classifier" here is a set of written rules that label a posting
fit / maybe / no for one candidate persona (undergraduate, targeting product
management, consulting, and operations roles). This script encodes the rubric
as code, runs it against a hand-labeled benchmark, and measures agreement with
the human labels.

Three rubric versions are run together to show the tuning loop:

  v1  the rubric as first written:
      target role types = product management, AI engineering, big tech (any
      function), consulting. Undergraduate degree gate. (A pay floor is part of
      the written rubric but the benchmark carries no salary data, so it is not
      applied here.)

  v2  criteria rewritten after reading v1's errors:
      target = product management, consulting, operations / supply chain.
      AI-engineering / ML-engineering IC roles -> "maybe" (coding-screen barrier).
      data science / data analyst / research roles -> "no".

  v3  v2 + company tier: an on-target PM / ops role at a lower-profile
      industrial / utility / insurance employer is downgraded fit -> maybe.

Usage:  python eval.py
"""
import csv
import collections

CORPUS = "data/postings.csv"

CONSULTING = {
    "mckinsey", "bain", "boston consulting", "bcg", "deloitte", "pwc",
    "pricewaterhousecoopers", "ernst & young", "kpmg", "accenture",
    "booz allen", "alixpartners", "alvarez & marsal",
}
BIG_TECH = {
    "google", "meta", "amazon", "microsoft", "apple", "nvidia", "netflix",
    "adobe", "databricks", "atlassian", "datadog", "notion", "roblox",
    "tiktok", "bytedance", "openai", "anthropic", "stripe",
}
PM_KW = [
    "product management", "product manager", " apm", "associate product",
    "product owner", "product development intern", "digital product",
    "technical product", "product innovation intern", "product intern",
    "product analyst", "offering management",
]
OPS_KW = [
    "operations", "supply chain", "logistics", "workforce management",
    "industrial engineer", "facilities", "process engineer",
]
AI_ENG_KW = [
    "ai engineer", "machine learning engineer", "ml engineer", "ai/ml engineer",
    "applied ai", "genai engineer", "generative ai intern", "ai intern",
    "deep learning", "autonomous vehicles and robotics",
]
DATA_KW = [
    "data scien", "data analy", "analytics", "data engineer", "data & integration",
    "data enablement", "research scientist", "machine learning research",
    "applied research", "applied math",
]
# lower-profile employers: on-target PM/ops fit -> maybe (v3 only)
LOWER_PROFILE = {
    "allied solutions", "ge vernova", "honeywell", "oshkosh", "vertiv",
    "chamberlain group", "springs window fashions", "atco", "corning",
    "edison international", "iat insurance group", "amgen", "rtx",
    "manulife financial", "nationwide", "royal bank of canada", "united airlines",
}


def _degs(degrees):
    return [d for d in degrees.split("/") if d and d != "(none listed)"]


def base(company, title, degrees):
    """Shared v2/v3 core: returns (decision, role_bucket) or (None, None)."""
    degs = _degs(degrees)
    if degs and "Bachelor's" not in degs:
        return "no", "degree-gate"
    t = title.lower()
    if any(k in t for k in DATA_KW):
        return "no", "data"
    if any(k in t for k in PM_KW):
        return "fit", "pm"
    if any(k in t for k in OPS_KW):
        return "fit", "ops"
    return None, None


def v1(company, title, degrees):
    c = company.lower()
    if _degs(degrees) and "Bachelor's" not in _degs(degrees):
        return "no"
    t = title.lower()
    if any(k in t for k in PM_KW):
        return "fit"
    if any(k in t for k in AI_ENG_KW):
        return "fit"
    if any(k in c for k in CONSULTING):
        return "fit"
    if c in BIG_TECH:
        return "fit"
    if any(k in t for k in DATA_KW):
        return "maybe"
    return "no"


def v2(company, title, degrees):
    c = company.lower()
    d, _ = base(company, title, degrees)
    if d is not None:
        return d
    if any(k in c for k in CONSULTING):
        return "fit"
    if any(k in title.lower() for k in AI_ENG_KW):
        return "maybe"
    return "no"


def v3(company, title, degrees):
    c = company.lower()
    d, bucket = base(company, title, degrees)
    if d == "fit" and bucket in ("pm", "ops") and c in LOWER_PROFILE:
        return "maybe"
    if d is not None:
        return d
    if any(k in c for k in CONSULTING):
        return "fit"
    if any(k in title.lower() for k in AI_ENG_KW):
        return "maybe"
    return "no"


def main():
    rows = [r for r in csv.DictReader(open(CORPUS, encoding="utf-8")) if r["label"].strip()]
    n = len(rows)
    cls = ["fit", "maybe", "no"]

    print(f"corpus: {n} labeled postings\n")
    print(f"{'version':<8}{'exact':>12}{'fit precision':>16}{'fit recall':>13}{'fit F1':>9}")
    results = {}
    for name, fn in [("v1", v1), ("v2", v2), ("v3", v3)]:
        exact = tp = fp = fn_ = 0
        cm = collections.Counter()
        diffs = []
        for r in rows:
            human = r["label"].strip().lower()
            pred = fn(r["company"], r["role"], r["degrees"])
            cm[(human, pred)] += 1
            if human == pred:
                exact += 1
            else:
                diffs.append((r["id"], r["company"], r["role"], human, pred))
            if pred == "fit" and human == "fit":
                tp += 1
            elif pred == "fit":
                fp += 1
            elif human == "fit":
                fn_ += 1
        prec = tp / (tp + fp) if tp + fp else 0
        rec = tp / (tp + fn_) if tp + fn_ else 0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
        results[name] = (exact, cm, diffs)
        print(f"{name:<8}{exact}/{n} = {exact / n:>5.0%}{prec:>15.0%}{rec:>13.0%}{f1:>9.2f}")

    for name in ("v1", "v3"):
        exact, cm, diffs = results[name]
        print(f"\n--- {name} confusion matrix (rows = human label, cols = rubric) ---")
        print("           " + "".join(f"{x:>8}" for x in cls))
        for h in cls:
            print(f"  {h:>7}  " + "".join(f"{cm[(h, x)]:>8}" for x in cls))
        print(f"{name} disagreements:")
        for cid, co, ro, h, p in diffs:
            print(f"  #{cid:>2}  {co[:22]:<22} {ro[:44]:<44} human={h:<5} rubric={p}")


if __name__ == "__main__":
    main()
