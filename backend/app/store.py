from pathlib import Path
from threading import Lock

from .models import Assessment


class AssessmentStore:
    def __init__(self) -> None:
        self._items: dict[str, Assessment] = {}
        self._paths: dict[str, tuple[list[Path], list[Path]]] = {}
        self._lock = Lock()

    def put(self, assessment: Assessment, question_pages: list[Path], answer_pages: list[Path]) -> None:
        with self._lock:
            self._items[assessment.id] = assessment
            self._paths[assessment.id] = (question_pages, answer_pages)

    def get(self, assessment_id: str) -> Assessment | None:
        with self._lock:
            return self._items.get(assessment_id)

    def paths(self, assessment_id: str) -> tuple[list[Path], list[Path]] | None:
        with self._lock:
            return self._paths.get(assessment_id)

    def update(self, assessment_id: str, **changes) -> Assessment:
        with self._lock:
            current = self._items[assessment_id]
            updated = current.model_copy(update=changes)
            self._items[assessment_id] = updated
            return updated


store = AssessmentStore()

