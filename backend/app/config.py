import os
from dataclasses import dataclass
from pathlib import Path


def _integer(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    max_upload_mb: int = _integer("MAX_UPLOAD_MB", 20)
    max_pages: int = _integer("MAX_PAGES", 20)
    data_dir: Path = Path(os.getenv("DATA_DIR", "/tmp/vedaai"))
    allowed_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:8080"
        ).split(",")
        if origin.strip()
    )


settings = Settings()

