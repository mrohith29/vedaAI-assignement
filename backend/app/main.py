import asyncio
import logging
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .ai import GeminiAnalyzer
from .config import settings
from .documents import save_and_render
from .models import Assessment, DocumentInfo, Health, QuestionResult
from .store import store


logger = logging.getLogger(__name__)
app = FastAPI(title="VedaAI Assessment Mapper", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=Health)
async def health() -> Health:
    return Health(status="ok", ai_configured=bool(settings.gemini_api_key))


@app.post("/api/assessments", response_model=Assessment, status_code=202)
async def create_assessment(
    question_paper: UploadFile = File(...),
    answer_sheet: UploadFile = File(...),
) -> Assessment:
    assessment_id = uuid4().hex
    root = settings.data_dir / assessment_id
    try:
        question_pages, answer_pages = await asyncio.gather(
            save_and_render(question_paper, root / "question"),
            save_and_render(answer_sheet, root / "answer"),
        )
    except Exception:
        _remove_tree(root)
        raise

    assessment = Assessment(
        id=assessment_id,
        status="queued",
        progress=10,
        stage="Documents prepared",
        question_paper=_document_info(assessment_id, "question", question_paper, question_pages),
        answer_sheet=_document_info(assessment_id, "answer", answer_sheet, answer_pages),
    )
    store.put(assessment, question_pages, answer_pages)
    asyncio.create_task(_process(assessment_id))
    return assessment


@app.get("/api/assessments/{assessment_id}", response_model=Assessment)
async def get_assessment(assessment_id: str) -> Assessment:
    assessment = store.get(assessment_id)
    if not assessment:
        raise HTTPException(404, "Assessment not found. It may have expired after a restart.")
    return assessment


@app.get("/api/assessments/{assessment_id}/pages/{document}/{page_number}.jpg")
async def get_page(assessment_id: str, document: str, page_number: int) -> FileResponse:
    paths = store.paths(assessment_id)
    if not paths or document not in {"question", "answer"}:
        raise HTTPException(404, "Page not found")
    pages = paths[0] if document == "question" else paths[1]
    if page_number < 1 or page_number > len(pages):
        raise HTTPException(404, "Page not found")
    return FileResponse(pages[page_number - 1], media_type="image/jpeg")


async def _process(assessment_id: str) -> None:
    paths = store.paths(assessment_id)
    if not paths:
        return
    question_pages, answer_pages = paths
    try:
        store.update(assessment_id, status="processing", progress=28, stage="Extracting questions")
        analyzer = GeminiAnalyzer()
        extracted = await asyncio.to_thread(analyzer.extract_questions, question_pages)
        store.update(assessment_id, progress=58, stage="Reading and mapping answers")
        mapped = await asyncio.to_thread(analyzer.map_answers, extracted, answer_pages)
        store.update(assessment_id, progress=88, stage="Preparing teacher review")

        by_id = {answer.question_id: answer for answer in mapped.answers}
        results: list[QuestionResult] = []
        for question in extracted.questions:
            answer = by_id.get(question.id)
            if answer is None:
                results.append(
                    QuestionResult(
                        **question.model_dump(), status="unanswered", answer_text="",
                        confidence=0, regions=[], score=None, feedback="No answer was identified."
                    )
                )
                continue
            question_data = question.model_dump(exclude={"max_score"})
            results.append(
                QuestionResult(
                    **question_data,
                    status=answer.status,
                    answer_text=answer.answer_text,
                    confidence=answer.confidence,
                    regions=answer.regions,
                    score=answer.score,
                    max_score=answer.max_score if answer.max_score is not None else question.max_score,
                    feedback=answer.feedback,
                )
            )

        store.update(
            assessment_id,
            status="completed",
            progress=100,
            stage="Review ready",
            questions=results,
            unmatched_answers=mapped.unmatched_answers,
            overall_feedback=mapped.overall_feedback,
        )
    except Exception as exc:
        logger.exception("Assessment processing failed: %s", assessment_id)
        message = (
            "Gemini is not configured. Add GEMINI_API_KEY and restart the service."
            if "GEMINI_API_KEY" in str(exc)
            else "Processing failed. Check the files and AI service configuration, then try again."
        )
        store.update(assessment_id, status="failed", stage="Processing failed", error=message)


def _document_info(
    assessment_id: str, document: str, upload: UploadFile, pages: list[Path]
) -> DocumentInfo:
    return DocumentInfo(
        filename=upload.filename or f"{document}.pdf",
        page_count=len(pages),
        page_urls=[
            f"/api/assessments/{assessment_id}/pages/{document}/{index}.jpg"
            for index in range(1, len(pages) + 1)
        ],
    )


def _remove_tree(root: Path) -> None:
    if not root.exists():
        return
    for child in sorted(root.rglob("*"), reverse=True):
        if child.is_file():
            child.unlink(missing_ok=True)
        elif child.is_dir():
            child.rmdir()
    root.rmdir()


static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
