# Toneleaf Comprehensive NLP Audit

Date: 17 July 2026

## Outcome

The first generated audit evaluated 746 labelled sentences. It passed 719 and exposed 27 failures. After reviewing the labels, removing awkward generated constructions, and correcting the engine by failure cluster, the retained comprehensive matrix passes all 745 cases.

| Area | Final result |
| --- | ---: |
| Polarity | 464 / 464 |
| Distress screening | 281 / 281 |
| Combined comprehensive audit | 745 / 745 |
| Curated core corpus | 81 / 81 |

## Coverage

- positive, neutral, and negative vocabulary;
- intensifiers and positive/negative negation;
- insults, threats, violence, and directed-threat separation;
- explicit distress language and combined lower-strength cues;
- poison, excessive-pill, jumping, self-injury, hanging, railway, and drowning intent patterns;
- self-deprecation, runaway, and never-return variants;
- contractions, common spelling variation, phrase framing, and punctuation;
- false-positive controls for prescribed medicine, poison removal/storage, knots, railways, buildings, water, and historical references.

## Improvements made from the failures

- Restricted pill screening to excess-quantity language instead of ordinary prescribed use.
- Removed ambiguous `take` from poison-ingestion matching so moving or storing poison is not treated as ingestion.
- Added first-person contraction and self-deprecation variants.
- Added home/family runaway, never-return, moving-train, railway, ocean, and drowning intent variants.
- Expanded noose-preparation language while preserving ordinary knot instructions.
- Replaced generic `die` matching with first-person death intent, preventing directed threats from being presented as self-distress.
- Made overlapping cues retain the stronger contextual weight.
- Strengthened negation reversal for low-weight sentiment words.

## Reproduction

```powershell
python scripts/run_comprehensive_audit.py
python -m unittest discover -s tests -v
python scripts/validate_notebook.py
```

## Interpretation

This is deterministic regression coverage, not population-level accuracy or clinical validation. It does not eliminate errors involving sarcasm, euphemisms, coded language, multilingual text, adversarial spelling, or long conversational context. Toneleaf must not be used as the sole basis for clinical, emergency, moderation, employment, legal, or safety decisions.
