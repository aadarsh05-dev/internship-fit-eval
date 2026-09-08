"""Regression tests for the fit rubric.

Locks the published baseline numbers (v1 46%, v2 74%, v3 82% exact-match
agreement on the 50-row benchmark) so a change to the rubric or the scorer
that moves them has to be deliberate. Standard library only:

    python -m unittest -v
"""
import csv
import unittest

import eval as E

ROWS = [r for r in csv.DictReader(open(E.CORPUS, encoding="utf-8")) if r["label"].strip()]


def agreement(fn):
    hits = sum(
        1 for r in ROWS
        if fn(r["company"], r["role"], r["degrees"]) == r["label"].strip().lower()
    )
    return hits, len(ROWS)


class Benchmark(unittest.TestCase):
    def test_corpus_shape(self):
        self.assertEqual(len(ROWS), 50)
        labels = [r["label"].strip().lower() for r in ROWS]
        self.assertEqual(labels.count("fit"), 14)
        self.assertEqual(labels.count("maybe"), 6)
        self.assertEqual(labels.count("no"), 30)

    def test_v1_baseline(self):
        self.assertEqual(agreement(E.v1), (23, 50))

    def test_v2_baseline(self):
        self.assertEqual(agreement(E.v2), (37, 50))

    def test_v3_baseline(self):
        self.assertEqual(agreement(E.v3), (41, 50))

    def test_monotonic_improvement(self):
        a1, a2, a3 = agreement(E.v1)[0], agreement(E.v2)[0], agreement(E.v3)[0]
        self.assertLess(a1, a2)
        self.assertLess(a2, a3)


class RubricRules(unittest.TestCase):
    def test_degree_gate_rejects_non_bachelors(self):
        # a posting that only accepts Master's / MBA is out for this persona
        for fn in (E.v2, E.v3):
            self.assertEqual(fn("Anywhere", "Product Manager Intern", "Master's/MBA"), "no")

    def test_degree_gate_passes_bachelors(self):
        for fn in (E.v2, E.v3):
            self.assertEqual(fn("Anywhere", "Product Manager Intern", "Bachelor's"), "fit")

    def test_missing_degrees_not_gated(self):
        for fn in (E.v2, E.v3):
            self.assertEqual(fn("Anywhere", "Product Manager Intern", "(none listed)"), "fit")

    def test_data_titles_rejected_in_v2_v3(self):
        for fn in (E.v2, E.v3):
            self.assertEqual(fn("Google", "Data Scientist Intern", "Bachelor's"), "no")

    def test_ai_eng_is_maybe_in_v2_v3(self):
        for fn in (E.v2, E.v3):
            self.assertEqual(fn("Meta", "Machine Learning Engineer Intern", "Bachelor's"), "maybe")

    def test_v3_downgrades_lower_profile_pm(self):
        # same on-target PM role: strong brand stays fit, lower-profile becomes maybe
        self.assertEqual(E.v3("American Express", "Product Development Intern", "Bachelor's"), "fit")
        self.assertEqual(E.v3("Honeywell", "Product Management Intern", "Bachelor's"), "maybe")

    def test_determinism(self):
        for fn in (E.v1, E.v2, E.v3):
            first = [fn(r["company"], r["role"], r["degrees"]) for r in ROWS]
            second = [fn(r["company"], r["role"], r["degrees"]) for r in ROWS]
            self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
