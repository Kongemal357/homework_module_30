import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.app import app
from src.database import Base, get_db
from src.models import Recipe  

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def session(engine):
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        yield session

@pytest.fixture
async def override_get_db(session):
    async def _override_get_db():
        yield session

    return _override_get_db

@pytest.fixture
async def client(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_recipes_empty(client):
    """Тестируем GET /recipes (если нет рецептов)"""
    response = await client.get("/recipes")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_post_recipe(client):
    """Тестируем POST /recipes (добавление нового рецепта)"""
    new_recipe = {
        "title": "Test Recipe",
        "cooking_time": 30,
        "ingredients": "Flour, Water, Salt",
        "description": "Simple test recipe",
    }
    response = await client.post("/recipes", json=new_recipe)
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["title"] == new_recipe["title"]
    assert json_data["cooking_time"] == new_recipe["cooking_time"]

@pytest.mark.asyncio
async def test_get_recipe_not_found(client):
    """Тестируем GET /recipes/{id} с несуществующим ID"""
    response = await client.get("/recipes/999")
    assert response.status_code == 200
    assert response.json() is None

@pytest.mark.asyncio
async def test_get_recipe_existing(client):
    """Тестируем GET /recipes/{id} с существующим рецептом"""
    new_recipe = {
        "title": "Test Recipe 2",
        "cooking_time": 45,
        "ingredients": "Eggs, Sugar, Flour",
        "description": "Another test recipe",
    }

    post_response = await client.post("/recipes", json=new_recipe)
    recipe_id = post_response.json()["id"]

    get_response = await client.get(f"/recipes/{recipe_id}")
    
    assert get_response.status_code == 200
    assert get_response.json()["title"] == new_recipe["title"]
