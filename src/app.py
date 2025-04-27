from contextlib import asynccontextmanager
from typing import List, Optional, Sequence

import src.models as models
import src.schemas as schemas
from src.database import close_engine, engine, get_session
from fastapi import Depends, FastAPI, Path
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    await close_engine()


app = FastAPI(lifespan=lifespan)


@app.get("/recipes", response_model=List[schemas.RecipesListOut])
async def get_recipes(
    session: AsyncSession = Depends(get_session),
) -> Sequence[models.Recipes]:
    recipe = await session.execute(select(models.Recipes))

    return recipe.scalars().all()


@app.get("/recipes/{id}", response_model=Optional[schemas.RecipeDetailOut])
async def get_recipe(
    id: int = Path(..., title="Id of the recipe", ge=0),
    session: AsyncSession = Depends(get_session),
) -> Optional[models.Recipes]:

    res = await session.execute(select(models.Recipes).where(models.Recipes.id == id))
    recipe = res.scalars().first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Item not found")

    await session.execute(
        update(models.Recipes)
        .where(models.Recipes.id == id)
        .values(views=models.Recipes.views + 1)
    )
    await session.commit()

    return recipe


@app.post("/recipes", response_model=schemas.RecipeDetailOut)
async def post_recipes(
    recipe: schemas.RecipesIn, session: AsyncSession = Depends(get_session)
) -> models.Recipes:
    new_recipe = models.Recipes(**recipe.model_dump())
    async with session.begin():
        session.add(new_recipe)
    return new_recipe
