from pathlib import Path

from google import genai
from google.genai import types

from .config import settings
from .models import AnswerMapping, QuestionExtraction


QUESTION_PROMPT = """
You are reading a printed question paper. Extract EVERY assessable question in printed order.
Rules:
- Preserve the exact visible number/label (for example `11 (a)`).
- Every labelled sub-part is a separate item. Unlabelled clauses that belong to the same prompt stay together.
- Do not invent missing text. Ignore headers, instructions, page numbers, and sample answers.
- Use the printed label as `id`; if a label repeats, append a short deterministic suffix.
- Include the printed maximum mark only when clearly shown.
The images follow, each preceded by its one-based page label.
""".strip()


ANSWER_PROMPT = """
You are mapping a handwritten answer sheet to an already extracted question list.
Return one answer record for EVERY supplied question, even if unanswered.
Rules:
- Answers may be written out of order, may omit their question label, and may span pages.
- Map by both visible labels and semantic content. Do not force unrelated work onto a question.
- `answer_text` is a faithful transcription; use [illegible] sparingly.
- For each contiguous answer block return its page and a tight normalized bounding box relative to the FULL page image.
  The coordinate origin is the page's TOP-LEFT: x increases to the right and y increases downward. x/y are the
  rectangle's left/top edges; width/height extend from those edges. Every value must be between 0 and 1.
- Locate the first and last handwritten line belonging to the answer, then box only that ink with roughly 0.5%
  page padding. Include the student's question label when present, but never include a neighboring question,
  page header, margin, or blank remainder of the page. Do not default to a full-width or full-page rectangle.
- If an answer continues after a large blank gap or on another page, return a separate tight region for every
  block. Before responding, visually re-check that each rectangle actually contains the transcribed answer text.
- `confidence` measures mapping confidence, not handwriting quality.
- Unanswered items have empty text, zero confidence, and no regions.
- Put substantial answer-like work that cannot map to any question in `unmatched_answers`.
- Grade conservatively only from the question and student work. If marks are unavailable, keep score/max_score null.
- Feedback should be concise, specific, and useful to a teacher.
""".strip()


class GeminiAnalyzer:
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        self.client = genai.Client(api_key=settings.gemini_api_key)

    def extract_questions(self, pages: list[Path]) -> QuestionExtraction:
        contents: list[object] = [QUESTION_PROMPT]
        contents.extend(_page_parts(pages, "Question paper"))
        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=QuestionExtraction,
            ),
        )
        return response.parsed or QuestionExtraction.model_validate_json(response.text)

    def map_answers(self, questions: QuestionExtraction, pages: list[Path]) -> AnswerMapping:
        question_context = questions.model_dump_json(indent=2)
        contents: list[object] = [
            f"{ANSWER_PROMPT}\n\nQuestion list:\n{question_context}"
        ]
        contents.extend(_page_parts(pages, "Answer sheet"))
        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=AnswerMapping,
            ),
        )
        return response.parsed or AnswerMapping.model_validate_json(response.text)


def _page_parts(pages: list[Path], label: str) -> list[object]:
    parts: list[object] = []
    for page_number, path in enumerate(pages, start=1):
        parts.append(f"{label} — page {page_number}")
        parts.append(types.Part.from_bytes(data=path.read_bytes(), mime_type="image/jpeg"))
    return parts
