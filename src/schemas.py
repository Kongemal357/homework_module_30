from pydantic import BaseModel, Field


class BaseRecipes(BaseModel):
    title: str = Field(..., title="Full title of the recipe")
    cooking_time: int = Field(..., title="Time required for cooking", ge=0)


class RecipesListOut(BaseRecipes):
    """Model for the recipe list"""

    views: int = Field(..., title="Number of times the recipe has been viewed", ge=0)

    class Config:
        from_attributes = True


class RecipeDetailOut(BaseRecipes):
    """Model for the recipe detail"""

    id: int = Field(..., title="Id of the recipe")
    ingredients: str = Field(..., title="Ingredients needed to prepare the recipe")
    description: str = Field(..., title="Description of recipe")

    class Config:
        from_attributes = True


class RecipesIn(BaseRecipes):
    """Model for create recipe"""

    views: int = Field(
        default=0, title="Number of times the recipe has been viewed", ge=0
    )
    ingredients: str = Field(..., title="Ingredients needed to prepare the recipe")
    description: str = Field(..., title="Description of recipe")
