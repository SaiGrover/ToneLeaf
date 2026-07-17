"""Run Toneleaf's 500+ sentence labelled audit and print a concise report."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.engine import analyze_distress, analyze_polarity
from tests.comprehensive_cases import DISTRESS_AUDIT_CASES, POLARITY_AUDIT_CASES


def evaluate(name: str, cases: list[tuple[str, str]], analyzer) -> tuple[int, list[str]]:
    failures = []
    for text, expected in cases:
        actual = analyzer(text)["label"]
        if actual != expected:
            failures.append(f"{name}: {text!r} expected={expected} actual={actual}")
    return len(cases) - len(failures), failures


def main() -> None:
    results = (
        ("polarity", POLARITY_AUDIT_CASES, analyze_polarity),
        ("distress", DISTRESS_AUDIT_CASES, analyze_distress),
    )
    total_correct = total_cases = 0
    all_failures: list[str] = []
    for name, cases, analyzer in results:
        correct, failures = evaluate(name, cases, analyzer)
        total_correct += correct
        total_cases += len(cases)
        all_failures.extend(failures)
        print(f"{name.capitalize()}: {correct}/{len(cases)}")
    print(f"Combined: {total_correct}/{total_cases}")
    if all_failures:
        print("\nFailures:")
        print("\n".join(all_failures))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
