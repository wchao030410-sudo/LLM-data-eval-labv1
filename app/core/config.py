from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LLM Data Eval Lab"
    app_env: str = "development"
    debug: bool = True

    database_url: str = "sqlite:///./llm_data_eval_lab.db"

    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    default_model: str = "gpt-4o-mini"
    enable_llm_judge: bool = False
    mock_mode: bool = True

    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "llm-data-eval-lab"

    upload_dir: str = "data/uploads"
    demo_data_dir: str = "data/demo"
    result_page_size: int = Field(default=50, ge=1, le=500)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
