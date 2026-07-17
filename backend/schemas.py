from typing import Literal

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5_000)
    mode: Literal["polarity", "distress"] = "polarity"


class ScoreSet(BaseModel):
    positive: int | None = None
    neutral: int | None = None
    negative: int | None = None
    supportive: int | None = None
    distress: int | None = None


class AnalysisResponse(BaseModel):
    scores: dict[str, int]
    label: str
    cues: list[str]
    confidence: int
    engine: str
    privacy: Literal["local-memory-only"] = "local-memory-only"
