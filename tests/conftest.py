import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.app import app
from src.database import Base, get_session

DATABASE_URL_TEST = "sqlite+aiosqlite:///./test.db"

engine_test = create_async_engine(DATABASE_URL_TEST, echo=True, future=True)
async_session_maker_test = async_sessionmaker(engine_test, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    """Создает таблицы перед тестами и удаляет после."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine_test.dispose()

@pytest.fixture(scope="function")
async def session() -> AsyncSession:
    """Создаёт новую сессию для каждого теста."""
    async with async_session_maker_test() as session:
        yield session

@pytest.fixture(scope="function", autouse=True)
async def override_get_session(session: AsyncSession):
    async def _get_test_session():
        yield session

    app.dependency_overrides[get_session] = _get_test_session

@pytest.fixture(scope="function")
async def client() -> AsyncClient:
    """Клиент для запросов к приложению."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
