import pytest
import pytest_asyncio
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from testcontainers.postgres import PostgresContainer
from src.orders.models import Base
from src.students.processed_event_repository import ProcessedEventRepository
from uuid import uuid4


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as container:
        yield container


@pytest.fixture(scope="session")
def db_url(postgres_container):
    return postgres_container.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql+asyncpg://")

@pytest_asyncio.fixture
async def session(db_url):
    engine = create_async_engine(db_url, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as s:
        yield s
        await s.rollback()
    await engine.dispose()


@pytest.fixture
def repo(session):
    return ProcessedEventRepository(session)


async def test_try_mark_processed_returns_true_for_new_event(repo):
    result = await repo.try_mark_processed(uuid4())
    assert result is True


async def test_try_mark_processed_returns_false_for_duplicate(repo):
    event_id = uuid4()
    await repo.try_mark_processed(event_id)
    result = await repo.try_mark_processed(event_id)
    assert result is False