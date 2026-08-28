import io
from pathlib import Path

import fitz
from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps

from .config import settings


ACCEPTED_TYPES = {"application/pdf", "image/jpeg", "image/png", "image/webp"}


async def save_and_render(upload: UploadFile, destination: Path) -> list[Path]:
    content_type = (upload.content_type or "").lower()
    if content_type not in ACCEPTED_TYPES:
        raise HTTPException(415, "Only PDF, PNG, JPEG, and WebP files are supported.")

    payload = await upload.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if not payload:
        raise HTTPException(400, f"{upload.filename or 'The uploaded file'} is empty.")
    if len(payload) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"Each file must be {settings.max_upload_mb} MB or smaller.")

    destination.mkdir(parents=True, exist_ok=True)
    try:
        if content_type == "application/pdf":
            pages = _render_pdf(payload, destination)
        else:
            pages = [_render_image(payload, destination / "page-1.jpg")]
    except (fitz.FileDataError, OSError, ValueError) as exc:
        raise HTTPException(422, "The file could not be read. Please upload a valid document.") from exc

    if len(pages) > settings.max_pages:
        raise HTTPException(422, f"Documents may contain at most {settings.max_pages} pages.")
    return pages


def _render_pdf(payload: bytes, destination: Path) -> list[Path]:
    document = fitz.open(stream=payload, filetype="pdf")
    if document.page_count > settings.max_pages:
        document.close()
        raise HTTPException(422, f"Documents may contain at most {settings.max_pages} pages.")

    rendered: list[Path] = []
    matrix = fitz.Matrix(2.0, 2.0)
    for index, page in enumerate(document):
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        target = destination / f"page-{index + 1}.jpg"
        pixmap.save(target, jpg_quality=88)
        rendered.append(target)
    document.close()
    if not rendered:
        raise ValueError("PDF contains no pages")
    return rendered


def _render_image(payload: bytes, target: Path) -> Path:
    with Image.open(io.BytesIO(payload)) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        image.thumbnail((2000, 2800), Image.Resampling.LANCZOS)
        image.save(target, "JPEG", quality=90, optimize=True)
    return target
