import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.app import app
from src.database import Base, get_session

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
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
    async with AsyncSession(engine) as session:
        yield session

@pytest.fixture
async def client(session):
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
async def test_recipe(session):
    from src.models import Recipe  
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

@pytest.mark.asyncio
async def test_post_recipe(client):
    """Тестируем POST /recipes (добавление нового рецепта)"""
    new_recipe = {
        "title": "New Test Recipe",
        "cooking_time": 25,
        "ingredients": "New ingredients",
        "description": "New description",
    }
    response = await client.post("/recipes", json=new_recipe)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == new_recipe["title"]
    assert data["cooking_time"] == new_recipe["cooking_time"]

@pytest.mark.asyncio
async def test_get_recipe_not_found(client):
    """Тестируем GET /recipes/{id} с несуществующим ID"""
    response = await client.get("/recipes/999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_recipe_existing(client, test_recipe):
    """Тестируем GET /recipes/{id} с существующим рецептом"""
    response = await client.get(f"/recipes/{test_recipe.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Recipe"
    assert data["cooking_time"] == 30

@pytest.mark.asyncio
async def test_update_recipe(client, test_recipe):
    """Тестируем PATCH /recipes/{id}"""
    update_data = {
        "title": "Updated Recipe",
        "cooking_time": 35
    }
    response = await client.patch(
        f"/recipes/{test_recipe.id}",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Recipe"
    assert data["cooking_time"] == 35

@pytest.mark.asyncio
async def test_delete_recipe(client, test_recipe):
    """Тестируем DELETE /recipes/{id}"""
    response = await client.get(f"/recipes/{test_recipe.id}")
    assert response.status_code == 200
    
    response = await client.delete(f"/recipes/{test_recipe.id}")
    assert response.status_code == 200
    
    response = await client.get(f"/recipes/{test_recipe.id}")
    assert response.status_code == 404
