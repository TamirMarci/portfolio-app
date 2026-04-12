from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    database_url: str = "sqlite:///./portfolio.db"
    price_cache_ttl_minutes: int = 15
    excel_file_path: str = str(Path(__file__).parent.parent.parent / "Portfolio.xlsx")
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = {"env_file": ".env"}


settings = Settings()
