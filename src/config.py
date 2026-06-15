from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: str = "postgresql+asyncpg://postgres:123456@127.0.0.1:5432/orders_db"
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600

settings = Settings()