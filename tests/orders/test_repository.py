import pytest
import pytest_asyncio
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from testcontainers.postgres import PostgresContainer
from src.orders.models import Base, OrderModel
from src.orders.repository import SQLAlchemyOrderRepository
from uuid import uuid4


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as container:
        yield container


@pytest.fixture(scope="session")
def db_url(postgres_container):
    return postgres_container.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql+asyncpg://"
    )


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
    return SQLAlchemyOrderRepository(session)


async def test_create_order(repo):
    order = OrderModel(title="Test", price=99.9)
    created = await repo.create(order)
    assert created.id == order.id
    assert created.title == "Test"


async def test_get_by_id_returns_order(repo):
    order = OrderModel(title="Find me", price=10.0)
    await repo.create(order)
    found = await repo.get_by_id(order.id)
    assert found is not None
    assert found.id == order.id


async def test_get_by_id_returns_none_if_not_exists(repo):
    result = await repo.get_by_id(uuid4())
    assert result is None


async def test_get_all_returns_list(repo):
    await repo.create(OrderModel(title="Order 1", price=1.0))
    await repo.create(OrderModel(title="Order 2", price=2.0))
    all_orders = await repo.get_all()
    assert len(all_orders) >= 2