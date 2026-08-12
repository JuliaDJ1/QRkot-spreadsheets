from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, PositiveInt, model_serializer


class DonationCreate(BaseModel):
    """Схема для создания пожертвования."""

    full_amount: PositiveInt
    comment: Optional[str] = None

    model_config = {'extra': 'forbid'}


class DonationDB(BaseModel):
    """Схема ответа при создании пожертвования (для владельца)."""

    id: int
    full_amount: PositiveInt
    comment: Optional[str] = None
    create_date: datetime

    model_config = {'from_attributes': True, 'extra': 'forbid'}

    @model_serializer
    def serialize(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'full_amount': self.full_amount,
            'comment': self.comment,
            'create_date': self.create_date,
        }


class DonationFullInfoDB(BaseModel):
    """Схема ответа с полными данными пожертвования (для суперпользователя)."""

    id: int
    full_amount: PositiveInt
    comment: Optional[str] = None
    user_id: Optional[int] = None
    create_date: datetime
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime] = None

    model_config = {'from_attributes': True, 'extra': 'forbid'}

    @model_serializer
    def serialize(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'full_amount': self.full_amount,
            'comment': self.comment,
            'user_id': self.user_id,
            'create_date': self.create_date,
            'invested_amount': self.invested_amount,
            'fully_invested': self.fully_invested,
            'close_date': self.close_date,
        }
