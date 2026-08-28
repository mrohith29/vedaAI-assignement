from typing import Literal

from pydantic import BaseModel, Field, field_validator


class BoundingBox(BaseModel):
    x: float = Field(ge=0, le=1, description="Left edge as a fraction of the full page width")
    y: float = Field(ge=0, le=1, description="Top edge as a fraction of the full page height")
    width: float = Field(ge=0, le=1, description="Horizontal distance from x to the right edge")
    height: float = Field(ge=0, le=1, description="Vertical distance from y to the bottom edge")

    @field_validator("width")
    @classmethod
    def clamp_width(cls, value: float, info):
        x = info.data.get("x", 0)
        return min(value, 1 - x)

    @field_validator("height")
    @classmethod
    def clamp_height(cls, value: float, info):
        y = info.data.get("y", 0)
        return min(value, 1 - y)


class AnswerRegion(BaseModel):
    page: int = Field(ge=1, description="One-based answer-sheet page number")
    bbox: BoundingBox = Field(description="Tight rectangle containing only this answer block")


class ExtractedQuestion(BaseModel):
    id: str = Field(description="Stable identifier, normally the printed question number")
    number: str = Field(description="Original printed numbering such as 11 (a)")
    text: str
    max_score: float | None = Field(default=None, ge=0)


class QuestionExtraction(BaseModel):
    questions: list[ExtractedQuestion]


class MappedAnswer(BaseModel):
    question_id: str
    status: Literal["answered", "unanswered"]
    answer_text: str = ""
    confidence: float = Field(default=0, ge=0, le=1)
    regions: list[AnswerRegion] = Field(default_factory=list)
    score: float | None = Field(default=None, ge=0)
    max_score: float | None = Field(default=None, ge=0)
    feedback: str = ""


class UnmatchedAnswer(BaseModel):
    label: str
    answer_text: str
    regions: list[AnswerRegion]


class AnswerMapping(BaseModel):
    answers: list[MappedAnswer]
    unmatched_answers: list[UnmatchedAnswer] = Field(default_factory=list)
    overall_feedback: str = ""


class QuestionResult(ExtractedQuestion):
    status: Literal["answered", "unanswered"]
    answer_text: str
    confidence: float
    regions: list[AnswerRegion]
    score: float | None
    feedback: str


class DocumentInfo(BaseModel):
    filename: str
    page_count: int
    page_urls: list[str]


class Assessment(BaseModel):
    id: str
    status: Literal["queued", "processing", "completed", "failed"]
    progress: int = Field(ge=0, le=100)
    stage: str
    error: str | None = None
    question_paper: DocumentInfo
    answer_sheet: DocumentInfo
    questions: list[QuestionResult] = Field(default_factory=list)
    unmatched_answers: list[UnmatchedAnswer] = Field(default_factory=list)
    overall_feedback: str = ""


class Health(BaseModel):
    status: str
    ai_configured: bool
