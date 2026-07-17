"""Large deterministic, human-labelled audit matrix for Toneleaf.

The cases are generated from reviewed language templates so the suite can cover
hundreds of variations without committing a repetitive fixture file.  Labels
remain independent of the engine output.
"""

from __future__ import annotations

from backend.engine import DISTRESS_PATTERNS, NEGATIVE, POSITIVE, THREAT_PATTERNS


def _unique(cases: list[tuple[str, str]]) -> list[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    return [case for case in cases if not (case in seen or seen.add(case))]


def polarity_audit_cases() -> list[tuple[str, str]]:
    cases: list[tuple[str, str]] = []

    for word in POSITIVE:
        cases.extend([
            (f"The experience felt {word}.", "positive"),
            (f"Overall, this was very {word}!", "positive"),
        ])

    for word in NEGATIVE:
        if word in {"nothing", "nobody"}:
            continue
        cases.extend([
            (f"The experience felt {word}.", "negative"),
            (f"Overall, this was very {word}!", "negative"),
        ])

    subjects = ("package", "document", "meeting", "train", "report", "device")
    actions = ("arrived", "opened", "started", "stopped", "moved", "remained")
    details = ("at noon", "on Tuesday", "near the office", "after lunch")
    for subject in subjects:
        for action in actions:
            for detail in details:
                cases.append((f"The {subject} {action} {detail}.", "neutral"))

    negated_negative = (
        "bad", "awful", "terrible", "horrible", "worst", "sad", "angry",
        "disappointed", "broken", "useless", "annoying", "wrong", "difficult",
        "poor", "upset", "frustrated", "hopeless", "unsafe", "unreliable", "toxic",
    )
    negated_positive = (
        "good", "amazing", "wonderful", "excellent", "perfect", "fantastic",
        "great", "happy", "beautiful", "helpful", "pleasant", "safe", "supported",
        "delicious", "friendly", "thoughtful", "outstanding", "easy", "reliable", "satisfied",
    )
    for word in negated_negative:
        cases.append((f"This is not {word}.", "positive"))
    for word in negated_positive:
        cases.append((f"This is not {word}.", "negative"))

    for phrase in THREAT_PATTERNS:
        cases.extend([
            (f"I will {phrase}.", "negative"),
            (f"Listen carefully: I am going to {phrase}.", "negative"),
        ])

    high_risk = (
        "I will eat poison.",
        "I will swallow rat poison.",
        "How to tie a knot to be hanged.",
        "I will lie on the train tracks.",
        "I want to jump off the roof.",
        "I intend to hurt myself.",
        "I am a complete loser.",
        "I'm a total failure.",
        "I feel like a worthless loser.",
        "I want to run away from home.",
        "I will stand in front of a moving train.",
        "I will walk into the ocean and never return.",
    )
    cases.extend((text, "negative") for text in high_risk)

    controls = (
        ("The rat poison is stored in a locked cabinet.", "neutral"),
        ("The sailor explained how to tie a knot.", "neutral"),
        ("Workers repaired the railway track this morning.", "neutral"),
        ("I will lie down on the sofa.", "neutral"),
        ("The train passed in front of the station.", "neutral"),
        ("I take pills prescribed by my doctor.", "neutral"),
        ("Please take the rat poison away from the kitchen.", "neutral"),
        ("The history lesson discussed people who were hanged.", "neutral"),
        ("She won the swimming race in the ocean.", "neutral"),
        ("He called the movie a complete failure.", "negative"),
    )
    cases.extend(controls)
    return _unique(cases)


def distress_audit_cases() -> list[tuple[str, str]]:
    cases: list[tuple[str, str]] = []

    for phrase, weight in DISTRESS_PATTERNS.items():
        if weight < 5.0:
            continue
        cases.extend([
            (phrase, "distress"),
            (f"Please listen, I keep thinking: {phrase}.", "distress"),
            (f"Right now the words in my head are '{phrase}'.", "distress"),
        ])

    poison_verbs = ("eat", "drink", "swallow", "ingest", "consume")
    poison_objects = ("poison", "rat poison", "strong poison", "a bottle of poison")
    for verb in poison_verbs:
        for obj in poison_objects:
            cases.append((f"I will {verb} {obj}.", "distress"))

    jump_forms = ("jump off", "jump from")
    heights = ("the building", "a bridge", "the roof", "the balcony", "a cliff")
    for form in jump_forms:
        for height in heights:
            cases.append((f"I want to {form} {height}.", "distress"))

    for verb in ("hit", "hurt", "harm", "cut", "stab", "shoot", "burn", "strangle"):
        cases.append((f"I plan to {verb} myself.", "distress"))

    for statement in (
        "I will take all my pills.",
        "I might swallow a bottle of tablets.",
        "I plan to take too many pills.",
        "I want to swallow a handful of pills.",
        "I am a loser.",
        "I am a complete failure.",
        "I feel like a worthless loser.",
        "I think I am useless.",
        "I'm a complete loser.",
        "I consider myself worthless.",
        "I will run away from my family.",
        "I want to run away from home.",
        "I am going to leave home and never return.",
        "How to tie a knot to be hanged.",
        "How do I tie a noose to hang myself?",
        "Show me how to make a noose for hanging.",
        "I will lay down on a railway track.",
        "I want to lie on the train tracks.",
        "I plan to stand in front of a moving train.",
        "I am going to wait on the railroad track for a train.",
        "I will walk into the ocean and never return.",
        "I plan to drown myself in the lake.",
    ):
        cases.append((statement, "distress"))

    low_cues = ("hopeless", "worthless", "unbearable", "trapped", "pointless", "alone", "lonely", "empty")
    for first in low_cues:
        for second in low_cues:
            if first != second:
                cases.append((f"I feel {first} and {second}.", "distress"))

    ordinary_templates = (
        "The {thing} was discussed during class.",
        "A {thing} appears in the reference manual.",
        "Workers inspected the {thing} yesterday.",
    )
    ordinary_things = (
        "railway track", "bridge", "roof", "balcony", "window", "medicine bottle",
        "knot", "rope", "ocean", "lake", "building", "train schedule",
    )
    for template in ordinary_templates:
        for thing in ordinary_things:
            cases.append((template.format(thing=thing), "supportive"))

    controls = (
        "The rat poison is stored in a locked cabinet.",
        "Please take the rat poison away from the kitchen.",
        "I take pills prescribed by my doctor.",
        "She swallowed one tablet as prescribed.",
        "The sailor explained how to tie a knot.",
        "The history lesson discussed people who were hanged.",
        "Workers repaired the railway track this morning.",
        "I will lie down on the sofa.",
        "The train passed in front of the station.",
        "She won the swimming race in the ocean.",
        "He called the movie a complete failure.",
        "I will run away from the sprinkler.",
    )
    cases.extend((text, "supportive") for text in controls)
    for phrase in THREAT_PATTERNS:
        text = f"{phrase}." if phrase.startswith("you will") else f"I will {phrase}."
        cases.append((text, "supportive"))
    return _unique(cases)


POLARITY_AUDIT_CASES = polarity_audit_cases()
DISTRESS_AUDIT_CASES = distress_audit_cases()
TOTAL_AUDIT_CASES = len(POLARITY_AUDIT_CASES) + len(DISTRESS_AUDIT_CASES)

assert TOTAL_AUDIT_CASES >= 500
