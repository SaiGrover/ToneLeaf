"""Local NLP engines used by Toneleaf.

The optional transformer is loaded only from an existing local directory.  This
module never downloads a model and never sends text over the network.
"""

from __future__ import annotations

import math
import os
import re
from functools import lru_cache
from pathlib import Path

TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?|[!?]+", re.IGNORECASE)

POSITIVE = {
    "love": 3.2, "loved": 3.2, "amazing": 3.2, "awesome": 3.1,
    "wonderful": 3.0, "excellent": 3.2, "perfect": 3.1,
    "fantastic": 3.2, "great": 2.5, "good": 1.9, "happy": 2.7,
    "joy": 2.8, "excited": 2.4, "beautiful": 2.5, "helpful": 1.8,
    "thanks": 1.5, "thank": 1.5, "pleased": 2.1, "best": 3.0,
    "brilliant": 2.8, "recommend": 2.1, "enjoy": 2.2, "calm": 1.5,
    "hope": 1.7, "safe": 1.7, "supported": 1.8, "delicious": 2.6,
    "friendly": 2.0, "pleasant": 2.1, "thoughtful": 2.2,
    "surprise": 1.2, "outstanding": 3.1, "proud": 2.5,
    "perfectly": 3.0, "easy": 1.5, "improvement": 2.2,
    "improved": 2.2, "happily": 1.8, "kind": 2.2, "grateful": 2.5,
    "successful": 2.5, "success": 2.4, "impressive": 2.4,
    "satisfied": 2.2, "satisfying": 2.2, "reliable": 1.8,
}
NEGATIVE = {
    "hate": -3.3, "hated": -3.3, "awful": -3.1, "terrible": -3.2,
    "horrible": -3.2, "worst": -3.4, "bad": -2.2, "sad": -2.3,
    "angry": -2.7, "disappointed": -2.6, "disappointing": -2.6,
    "broken": -2.1, "fail": -2.4, "failed": -2.4, "failure": -2.6,
    "useless": -2.5, "annoying": -1.9, "problem": -1.6, "wrong": -1.7,
    "difficult": -1.3, "poor": -2.0, "upset": -2.1,
    "frustrated": -2.0, "regret": -2.2, "pain": -2.1,
    "lonely": -2.4, "hopeless": -3.1, "exhausted": -1.8,
    "empty": -1.7, "worthless": -3.2, "kill": -4.0, "killed": -4.0,
    "murder": -4.5, "murdered": -4.5, "attack": -3.2, "attacked": -3.2,
    "harm": -3.0, "hurt": -2.8, "threat": -3.0, "threaten": -3.4,
    "threatened": -3.4, "destroy": -2.8, "violent": -3.2, "violence": -3.2,
    "disgusting": -3.4, "disgusted": -3.2, "rude": -2.7,
    "insult": -2.8, "insulting": -3.0, "unacceptable": -3.1,
    "waste": -2.8, "boring": -2.0, "slow": -1.3, "painfully": -1.6,
    "terrified": -3.3, "unsafe": -3.0, "dishonest": -3.0, "scam": -3.5,
    "unreliable": -2.4, "nothing": -1.2, "nobody": -1.4,
    "cruel": -3.2, "offensive": -2.8, "toxic": -3.0, "abusive": -3.5,
    "disaster": -3.2, "disastrous": -3.2, "pathetic": -3.2,
    "ridiculous": -2.5, "incompetent": -3.0, "deceitful": -3.0,
    "loser": -3.2, "looser": -3.2,
}
LEXICON = POSITIVE | NEGATIVE
INTENSIFIERS = {"very", "really", "extremely", "absolutely", "so", "incredibly", "deeply", "totally"}
NEGATORS = {"not", "no", "never", "hardly", "isn't", "wasn't", "don't", "didn't", "can't", "cannot", "won't"}

THREAT_PATTERNS = {
    "kill you": 6.0, "kill him": 5.5, "kill her": 5.5, "kill them": 5.5,
    "murder you": 6.0, "hurt you": 4.5, "harm you": 4.5,
    "attack you": 4.5, "destroy you": 4.0, "you will die": 5.5,
    "going to kill": 5.5, "gonna kill": 5.5,
}

NEGATIVE_PATTERNS = {
    "nobody cares": 3.2, "complete waste": 3.2, "not good enough": 2.8,
    "piece of trash": 3.5, "piece of garbage": 3.5, "shut up": 2.3,
}

DISTRESS_PATTERNS = {
    "kill myself": 6.0, "end my life": 6.0, "cannot go on": 5.0,
    "can't go on": 5.0, "suicidal": 5.0, "suicide": 5.0,
    "want to die": 5.0, "self harm": 5.0, "hurt myself": 5.0,
    "kill me": 5.5, "hit myself": 5.0, "cut myself": 5.0,
    "harm myself": 5.0, "shoot myself": 6.0, "stab myself": 6.0,
    "hang myself": 6.0, "throw myself": 5.0, "overdose": 5.0,
    "end it all": 5.0, "don't want to live": 5.0,
    "do not want to live": 5.0, "wish i were dead": 5.0,
    "wish i was dead": 5.0, "better off dead": 5.0,
    "jump from the building": 5.5, "jump from a building": 5.5,
    "jump from building": 5.5, "jump off the building": 5.5,
    "jump off a building": 5.5, "jump off the bridge": 5.5,
    "jump off a bridge": 5.5, "jump from the roof": 5.5,
    "jump off the roof": 5.5, "jump out of the window": 5.5,
    "jump out the window": 5.5,
    "give up": 3.0, "hopeless": 3.0,
    "worthless": 3.0, "unbearable": 3.0, "trapped": 2.5,
    "no reason": 2.5, "pointless": 3.0, "alone": 2.5,
    "lonely": 2.0, "empty": 2.0, "numb": 2.0, "exhausted": 1.5,
}

# Contextual patterns require an action or first-person intent. This prevents a
# method noun by itself (for example, stored rat poison) from being treated as
# proof of distress.
DISTRESS_REGEX_PATTERNS = (
    (
        re.compile(
            r"\b(?:eat|drink|swallow|ingest|consume)\b"
            r"(?:\s+[a-z']+){0,5}\s+\b(?:rat\s+)?poison\b",
            re.IGNORECASE,
        ),
        6.0,
    ),
    (
        re.compile(
            r"\bjump(?:ing)?\s+(?:off|from|out\s+of)\b"
            r"(?:\s+[a-z']+){0,4}\s+\b"
            r"(?:building|bridge|roof|window|balcony|cliff)\b",
            re.IGNORECASE,
        ),
        5.5,
    ),
    (
        re.compile(
            r"\b(?:hit|hurt|harm|cut|stab|shoot|burn|hang|strangle)\s+"
            r"(?:myself|me)\b",
            re.IGNORECASE,
        ),
        5.5,
    ),
    (
        re.compile(
            r"\b(?:take|swallow)\s+(?:"
            r"(?:all|too\s+many|dozens\s+of)\s+(?:(?:my|the)\s+)?(?:pills|tablets)"
            r"|(?:a\s+)?(?:bottle|handful)\s+of\s+(?:pills|tablets)"
            r")\b",
            re.IGNORECASE,
        ),
        5.0,
    ),
    (
        re.compile(
            r"\bi(?:'m|\s+am|\s+feel(?:\s+like)?|\s+think\s+i\s+am)\s+"
            r"(?:a\s+)?(?:(?:complete|total|worthless|useless)\s+){0,2}"
            r"(?:loser|looser|failure|worthless|useless)\b",
            re.IGNORECASE,
        ),
        5.0,
    ),
    (
        re.compile(
            r"\bi\s+(?:will|want\s+to|am\s+going\s+to|plan\s+to)\s+"
            r"run\s+away\s+from\s+(?:(?:my|the)\s+)?(?:family|home)\b",
            re.IGNORECASE,
        ),
        5.0,
    ),
    (
        re.compile(
            r"\b(?:how\s+to|how\s+do\s+i|learn\s+to|show\s+me\s+how\s+to)\s+"
            r"(?:tie|make)\s+(?:a\s+)?(?:noose|knot)\b(?:\s+[a-z']+){0,5}\s+"
            r"\b(?:hang|hanged|hanging|strangle|strangled)\b",
            re.IGNORECASE,
        ),
        6.0,
    ),
    (
        re.compile(
            r"\bi\s+(?:will|want\s+to|plan\s+to|am\s+going\s+to)\s+"
            r"(?:lie|lay)(?:\s+down)?\s+on\s+(?:a|the)\s+"
            r"(?:railway|railroad|train)\s+tracks?\b",
            re.IGNORECASE,
        ),
        6.0,
    ),
    (
        re.compile(
            r"\bi\s+(?:will|want\s+to|plan\s+to|am\s+going\s+to)\s+"
            r"(?:stand|wait)\s+(?:in\s+front\s+of\s+(?:a\s+)?(?:moving\s+)?train"
            r"|on\s+(?:a|the)\s+(?:railway|railroad|train)\s+tracks?(?:\s+for\s+a\s+train)?)\b",
            re.IGNORECASE,
        ),
        6.0,
    ),
    (
        re.compile(
            r"\bi\s+(?:will|want\s+to|plan\s+to|am\s+going\s+to)\s+"
            r"(?:walk\s+into\s+(?:the\s+)?(?:ocean|sea|lake)\s+and\s+never\s+return"
            r"|drown\s+myself(?:\s+in\s+(?:the\s+)?(?:ocean|sea|lake))?)\b",
            re.IGNORECASE,
        ),
        6.0,
    ),
    (
        re.compile(
            r"\bi\s+(?:am\s+going\s+to|will|want\s+to|plan\s+to)\s+"
            r"leave\s+home\s+and\s+never\s+return\b",
            re.IGNORECASE,
        ),
        5.0,
    ),
    (
        re.compile(r"\bi\s+consider\s+myself\s+(?:worthless|useless|a\s+failure)\b", re.IGNORECASE),
        5.0,
    ),
    (
        re.compile(
            r"\bi\s+(?:will|want\s+to|plan\s+to|am\s+going\s+to|hope\s+to|wish\s+to)\s+"
            r"(?:[a-z']+\s+){0,3}(?:die|be\s+dead)\b|\bi(?:'m|\s+am)\s+dying\b",
            re.IGNORECASE,
        ),
        5.0,
    ),
)


def _percentages(values: dict[str, float]) -> dict[str, int]:
    total = sum(values.values()) or 1.0
    raw = {key: value * 100 / total for key, value in values.items()}
    rounded = {key: math.floor(value) for key, value in raw.items()}
    remaining = 100 - sum(rounded.values())
    order = sorted(raw, key=lambda key: raw[key] - rounded[key], reverse=True)
    for key in order[:remaining]:
        rounded[key] += 1
    return rounded


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def _phrase_hits(text: str, patterns: dict[str, float]) -> list[tuple[str, float]]:
    lower = text.lower().replace("’", "'")
    hits = []
    for phrase, weight in patterns.items():
        if re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", lower):
            hits.append((phrase, weight))
    return hits


def _distress_hits(text: str) -> list[tuple[str, float]]:
    """Return de-duplicated exact and contextual distress cues."""
    hits = _phrase_hits(text, DISTRESS_PATTERNS)
    lower = text.lower().replace("â€™", "'")
    for pattern, weight in DISTRESS_REGEX_PATTERNS:
        for match in pattern.finditer(lower):
            cue = " ".join(match.group(0).split())
            overlap_indexes = [
                index
                for index, (existing, _existing_weight) in enumerate(hits)
                if existing in cue or cue in existing
            ]
            if overlap_indexes:
                if max(hits[index][1] for index in overlap_indexes) >= weight:
                    continue
                hits = [
                    hit for index, hit in enumerate(hits)
                    if index not in overlap_indexes
                ]
            hits.append((cue, weight))
    return hits


def _cue_words(text: str, limit: int = 5) -> list[str]:
    hits: dict[str, float] = {}
    for phrase, weight in _phrase_hits(text, THREAT_PATTERNS):
        hits[phrase] = weight
    for phrase, weight in _phrase_hits(text, NEGATIVE_PATTERNS):
        hits[phrase] = weight
    for phrase, weight in _distress_hits(text):
        if weight >= 5.0:
            hits[phrase] = weight
    for token in _tokens(text):
        if token in LEXICON:
            hits[token] = max(abs(LEXICON[token]), hits.get(token, 0.0))
    return [word for word, _ in sorted(hits.items(), key=lambda item: item[1], reverse=True)[:limit]]


def _fallback_polarity(text: str) -> dict:
    tokens = _tokens(text)
    positive = negative = 0.0
    negative += sum(weight for _, weight in _phrase_hits(text, THREAT_PATTERNS))
    negative += sum(weight for _, weight in _phrase_hits(text, NEGATIVE_PATTERNS))
    # High-risk intent stays negative even when words like "good" or "healthy"
    # would otherwise dominate a generic sentiment score.
    negative += sum(weight * 1.5 for _, weight in _distress_hits(text) if weight >= 5.0)
    for index, word in enumerate(tokens):
        if word not in LEXICON:
            continue
        value = LEXICON[word]
        if index and tokens[index - 1] in INTENSIFIERS:
            value *= 1.45
        if any(token in NEGATORS for token in tokens[max(0, index - 3):index]):
            value *= -1.0
        if value > 0:
            positive += value
        else:
            negative += abs(value)

    emphasis = min(text.count("!") * 0.35, 1.4)
    if positive >= negative and positive:
        positive += emphasis
    elif negative:
        negative += emphasis
    neutral = max(1.2, len(tokens) * 0.12)
    if not positive and not negative:
        neutral = max(4.0, len(tokens) * 0.3)
    scores = _percentages({"positive": positive, "neutral": neutral, "negative": negative})
    label = max(scores, key=scores.get)
    return {
        "scores": scores,
        "label": label,
        "cues": _cue_words(text),
        "confidence": scores[label],
        "engine": "python-local-lexicon",
    }


@lru_cache(maxsize=1)
def _local_transformer():
    model_path = os.getenv("TONELEAF_MODEL_PATH", "").strip()
    if not model_path or not Path(model_path).is_dir():
        return None
    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)
        return pipeline("text-classification", model=model, tokenizer=tokenizer, top_k=None)
    except (ImportError, OSError, ValueError):
        return None


def analyze_polarity(text: str) -> dict:
    # Apply the safety-aware contextual layer consistently even when an optional
    # local transformer has been configured.
    if any(weight >= 5.0 for _, weight in _distress_hits(text)):
        return _fallback_polarity(text)

    classifier = _local_transformer()
    if classifier is None:
        return _fallback_polarity(text)

    predictions = classifier(text[:5_000], truncation=True)[0]
    aliases = {
        "label_0": "negative", "label_1": "neutral", "label_2": "positive",
        "negative": "negative", "neutral": "neutral", "positive": "positive",
    }
    values = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
    for prediction in predictions:
        label = aliases.get(str(prediction["label"]).lower())
        if label:
            values[label] += float(prediction["score"])
    if not any(values.values()):
        return _fallback_polarity(text)
    scores = _percentages(values)
    label = max(scores, key=scores.get)
    return {
        "scores": scores,
        "label": label,
        "cues": _cue_words(text),
        "confidence": scores[label],
        "engine": "python-local-transformer",
    }


def analyze_distress(text: str) -> dict:
    weighted = 0.0
    cues = []
    for phrase, weight in _distress_hits(text):
        weighted += weight
        cues.append(phrase)
    polarity = analyze_polarity(text)
    weighted += max(0, polarity["scores"]["negative"] - 35) / 20
    risk = min(96, round(5 + weighted * 9))
    scores = {"supportive": 100 - risk, "distress": risk}
    label = "distress" if risk >= 50 else "supportive"
    return {
        "scores": scores,
        "label": label,
        "cues": cues[:5],
        "confidence": max(scores.values()),
        "engine": f"python-local-screening+{polarity['engine']}",
    }


def analyze(text: str, mode: str) -> dict:
    return analyze_distress(text) if mode == "distress" else analyze_polarity(text)
