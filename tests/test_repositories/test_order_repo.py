import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.infrastructure.db.models import Base
from src.infrastructure.db.order_repo_impl import SQLAlchemyOrderRepository
from src.domain.entities.order import Order
from uuid import uuid4

TEST_DB_URL = "postgresql+asyncpg://postgres:123456@127.0.0.1:5433/postgres"


@pytest.fixture
async def engine():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def session(engine):
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as s:
        yield s
        await s.rollback()


@pytest.fixture
def repo(session):
    return SQLAlchemyOrderRepository(session)


async def test_create_order(repo):
    order = Order(title="Test", price=99.9)
    created = await repo.create(order)
    assert created.id == order.id
    assert created.title == "Test"


async def test_get_by_id_returns_order(repo):
    order = Order(title="Find me", price=10.0)
    await repo.create(order)
    found = await repo.get_by_id(order.id)
    assert found is not None
    assert found.id == order.id


async def test_get_by_id_returns_none_if_not_exists(repo):
    result = await repo.get_by_id(uuid4())
    assert result is None


async def test_get_all_returns_list(repo):
    await repo.create(Order(title="Order 1", price=1.0))
    await repo.create(Order(title="Order 2", price=2.0))
    all_orders = await repo.get_all()
    assert len(all_orders) >= 2