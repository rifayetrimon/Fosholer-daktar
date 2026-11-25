from functools import lru_cache
from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    APP_NAME: str = "fosholer daktar"
    DEBUG: bool = False

    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: SecretStr = SecretStr("postgres")
    DB_NAME: str = "fosholer_daktar"
    DB_SCHEMA: str = "fosholer_daktar"
    DB_SSL: bool = False

    SECRET_KEY: SecretStr = SecretStr("")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    GEMINI_API_KEY: SecretStr = SecretStr("")
    GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDINGS_URL: str = "gemini-embedding-001"
    EMBEDDING_DIM: int = 3072

    GROQ_API_KEY: SecretStr = SecretStr("")
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    HF_TOKEN: str = ""
    HF_MODEL_ID: str = "wambugu71/crop_leaf_diseases_vit"

    @model_validator(mode="after")
    def check_required_secrets(self) -> "Settings":
        if not self.SECRET_KEY.get_secret_value():
            raise ValueError("SECRET_KEY is required. Set it in your .env file.")
        if not self.GEMINI_API_KEY.get_secret_value():
            raise ValueError("GEMINI_API_KEY is required. Set it in your .env file.")
        if not self.GROQ_API_KEY.get_secret_value():
            raise ValueError("GROQ_API_KEY is required. Set it in your .env file.")
        return self

    @property
    def DATABASE_URL(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_PASSWORD.get_secret_value(),
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings():
    return Settings()
