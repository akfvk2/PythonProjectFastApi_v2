from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: str = "postgresql+asyncpg://postgres:123456@127.0.0.1:5432/orders_db"
    kafka_bootstrap_servers: str = "localhost:9092"
    student_events_topic: str = "student-events"
    student_events_dlq_topic: str = "student-events-dlq"
    student_events_group_id: str = "order-service-student-events"
    dedup_ttl_seconds: int = 86400
    max_attempts: int = 3
    retry_delay_seconds: int = 1
    max_poll_interval_seconds: int = 300
    max_retry_delay_seconds: int = 10
    student_events_retry_topic: str = "student-events-retry"
    student_events_retry_group_id: str = "order-service-student-events-retry"
    retry_budget_safety_margin: float = 0.5
    db_error_retry_delay_seconds: float = 5.0
    retry_tier_1_topic: str = "student-events-retry-tier1"
    retry_tier_1_delay_seconds: float = 5.0
    retry_tier_1_group_id: str = "order-service-retry-tier1"
    retry_tier_2_topic: str = "student-events-retry-tier2"
    retry_tier_2_delay_seconds: float = 30.0
    retry_tier_2_group_id: str = "order-service-retry-tier2"


settings = Settings()