import unittest

from backend.engine import analyze_distress, analyze_polarity
from tests.evaluation_cases import DISTRESS_CASES, POLARITY_CASES


class EvaluationCorpusTests(unittest.TestCase):
    def test_all_labelled_polarity_sentences(self):
        failures = []
        for text, expected in POLARITY_CASES:
            actual = analyze_polarity(text)["label"]
            if actual != expected:
                failures.append(f"{text!r}: expected {expected}, got {actual}")
        self.assertFalse(failures, "\n" + "\n".join(failures))

    def test_all_labelled_distress_sentences(self):
        failures = []
        for text, expected in DISTRESS_CASES:
            actual = analyze_distress(text)["label"]
            if actual != expected:
                failures.append(f"{text!r}: expected {expected}, got {actual}")
        self.assertFalse(failures, "\n" + "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
