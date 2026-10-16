from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    OPENAI_RECEIPT_MODEL: str = "gpt-4o-mini"
    RECEIPT_ANALYSIS_TIMEOUT_SECONDS: int = 45
    MAX_UPLOAD_BYTES: int = 8388608
    MAX_IMAGE_PIXELS: int = 20000000

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
