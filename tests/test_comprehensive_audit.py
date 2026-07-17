import unittest

from backend.engine import analyze_distress, analyze_polarity
from tests.comprehensive_cases import (
    DISTRESS_AUDIT_CASES,
    POLARITY_AUDIT_CASES,
    TOTAL_AUDIT_CASES,
)


class ComprehensiveAuditTests(unittest.TestCase):
    def test_audit_contains_more_than_500_sentences(self):
        self.assertGreaterEqual(TOTAL_AUDIT_CASES, 500)

    def test_comprehensive_polarity_matrix(self):
        failures = []
        for text, expected in POLARITY_AUDIT_CASES:
            actual = analyze_polarity(text)["label"]
            if actual != expected:
                failures.append(f"{text!r}: expected {expected}, got {actual}")
        self.assertFalse(failures, "\n" + "\n".join(failures))

    def test_comprehensive_distress_matrix(self):
        failures = []
        for text, expected in DISTRESS_AUDIT_CASES:
            actual = analyze_distress(text)["label"]
            if actual != expected:
                failures.append(f"{text!r}: expected {expected}, got {actual}")
        self.assertFalse(failures, "\n" + "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
