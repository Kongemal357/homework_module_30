import pytest
from src.app import app
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_get_recipes_empty():
    """Тестируем GET /recipes (если нет рецептов)"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/recipes")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_post_recipe():
    """Тестируем POST /recipes (добавление нового рецепта)"""
    new_recipe = {
        "title": "Test Recipe",
        "cooking_time": 30,
        "ingredients": "Flour, Water, Salt",
        "description": "Simple test recipe",
    }
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/recipes", json=new_recipe)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["title"] == new_recipe["title"]
    assert json_data["cooking_time"] == new_recipe["cooking_time"]


@pytest.mark.asyncio
async def test_get_recipe_not_found():
    """Тестируем GET /recipes/{id} с несуществующим ID"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/recipes/999")
    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.asyncio
async def test_get_recipe_existing():
    """Тестируем GET /recipes/{id} с существующим рецептом"""
    new_recipe = {
        "title": "Test Recipe 2",
        "cooking_time": 45,
        "ingredients": "Eggs, Sugar, Flour",
        "description": "Another test recipe",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        post_response = await client.post("/recipes", json=new_recipe)
        recipe_id = post_response.json()["id"]

        get_response = await client.get(f"/recipes/{recipe_id}")

    assert get_response.status_code == 200
    assert get_response.json()["title"] == new_recipe["title"]
