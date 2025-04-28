import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import client, test_recipe

@pytest.mark.asyncio
async def test_get_list_of_recipes(client, test_recipe):
    """Тестируем GET /recipes/{id}"""
    response = await client.get(f"/recipes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

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
    
    response = await client.get(f"/recipes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

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
