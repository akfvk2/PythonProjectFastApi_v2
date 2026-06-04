from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: str = "postgresql+psycopg://postgres:123456@127.0.0.1:5433/postgres"
    first_service_url: str = "http://localhost:8000"
    redis_url: str = "redis://localhost:6379"

settings = Settings()