import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import app
from src.database import Base, get_session
from src.models import Recipe


@pytest.fixture(scope="function")
async def db_session():
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

@pytest.fixture
async def client(db_session):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
async def test_recipe(db_session):
    recipe = Recipe(
        title="Test Recipe",
        cooking_time=30,
        ingredients="Test ingredients",
        description="Test description",
        views=0
    )
    db_session.add(recipe)
    await db_session.commit()
    return recipe

# Тесты
@pytest.mark.asyncio
async def test_post_recipe(client):
    """Тестируем POST /recipes"""
    new_recipe = {
        "title": "New Recipe",
        "cooking_time": 25,
        "ingredients": "New ingredients",
        "description": "New description",
    }
    response = await client.post("/recipes", json=new_recipe)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == new_recipe["title"]

@pytest.mark.asyncio
async def test_get_recipe_not_found(client):
    """Тестируем GET /recipes/{id} с несуществующим ID"""
    response = await client.get("/recipes/999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_recipe_existing(client, test_recipe):
    """Тестируем GET /recipes/{id}"""
    response = await client.get(f"/recipes/{test_recipe.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Recipe"

@pytest.mark.asyncio
async def test_update_recipe(client, test_recipe):
    """Тестируем PATCH /recipes/{id}"""
    update_data = {"title": "Updated Recipe"}
    response = await client.patch(
        f"/recipes/{test_recipe.id}",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Recipe"

@pytest.mark.asyncio
async def test_delete_recipe(client, test_recipe):
    """Тестируем DELETE /recipes/{id}"""
    response = await client.get(f"/recipes/{test_recipe.id}")
    assert response.status_code == 200
    
    response = await client.delete(f"/recipes/{test_recipe.id}")
    assert response.status_code == 200
    
    response = await client.get(f"/recipes/{test_recipe.id}")
    assert response.status_code == 404
