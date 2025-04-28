from src.database import Base

from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column


class Recipes(Base):
    __tablename__ = "recipes"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(20), nullable=False)
    views: Mapped[int] = mapped_column(nullable=False, default=0)
    cooking_time: Mapped[int] = mapped_column(nullable=False)
    ingredients: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(50), nullable=False)
