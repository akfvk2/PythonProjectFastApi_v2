from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: str = "postgresql+asyncpg://postgres:123456@127.0.0.1:5432/orders_db"
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600
    kafka_bootstrap_servers: str = "localhost:9092"
    student_events_topic: str = "student-events"
    student_events_dlq_topic: str = "student-events-dlq"
    student_events_group_id: str = "order-service-student-events"
    dedup_ttl_seconds: int = 86400

settings = Settings()