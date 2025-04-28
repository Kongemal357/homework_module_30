import pytest_asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.app import app
from src.database import Base, get_session
from src.models import Recipes

DATABASE_URL_TEST = "sqlite+aiosqlite:///./test.db"

engine_test = create_async_engine(DATABASE_URL_TEST, echo=True, future=True)
async_session_maker_test = async_sessionmaker(engine_test, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    """Создает таблицы перед тестами и удаляет после."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine_test.dispose()

@pytest_asyncio.fixture(scope="function")
async def session() -> AsyncSession:
    """Создаёт новую сессию для каждого теста."""
    async with async_session_maker_test() as session:
        yield session

@pytest_asyncio.fixture(scope="function", autouse=True)
async def override_get_session(session: AsyncSession):
    async def _get_test_session():
        yield session

    app.dependency_overrides[get_session] = _get_test_session

@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncClient:
    """Клиент для запросов к приложению."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def test_recipe(session):
    recipe = Recipe(
        title="Test Recipe",
        cooking_time=30,
        ingredients="Test ingredients",
        description="Test description",
        views=0
    )
    session.add(recipe)
    await session.commit()
    return recipe
