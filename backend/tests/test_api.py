from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


client = TestClient(app)


def image_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (32, 32), "white").save(buffer, "PNG")
    return buffer.getvalue()


def test_health_reports_configuration() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert isinstance(response.json()["ai_configured"], bool)


def test_rejects_unsupported_file() -> None:
    response = client.post(
        "/api/assessments",
        files={
            "question_paper": ("paper.txt", b"hello", "text/plain"),
            "answer_sheet": ("answer.png", image_bytes(), "image/png"),
        },
    )
    assert response.status_code == 415


def test_accepts_images_and_creates_job() -> None:
    response = client.post(
        "/api/assessments",
        files={
            "question_paper": ("paper.png", image_bytes(), "image/png"),
            "answer_sheet": ("answer.png", image_bytes(), "image/png"),
        },
    )
    assert response.status_code == 202
    payload = response.json()
    assert payload["question_paper"]["page_count"] == 1
    assert payload["answer_sheet"]["page_count"] == 1

