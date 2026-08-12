from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt


class CharityProjectCreate(BaseModel):
    """Схема для создания целевого проекта."""

    name: str = Field(min_length=5, max_length=100)
    description: str = Field(min_length=10)
    full_amount: PositiveInt

    model_config = {'extra': 'forbid'}


class CharityProjectUpdate(BaseModel):
    """Схема для редактирования целевого проекта."""

    name: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=10)
    full_amount: Optional[PositiveInt] = None

    model_config = {'extra': 'forbid'}


class CharityProjectDB(CharityProjectCreate):
    """Схема ответа с полными данными проекта из БД."""

    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime] = None

    model_config = {'from_attributes': True, 'extra': 'forbid'}
