from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.donation import Donation
from app.models.user import User


class CRUDDonation(CRUDBase[Donation]):
    """CRUD-операции для пожертвований."""

    async def get_not_fully_invested(
        self,
        session: AsyncSession,
    ) -> List[Donation]:
        """Получить нераспределённые пожертвования по дате создания."""
        result = await session.execute(
            select(Donation)
            .where(Donation.fully_invested.is_(False))
            .order_by(Donation.create_date)
        )
        return result.scalars().all()

    async def get_by_user(
        self,
        user: User,
        session: AsyncSession,
    ) -> List[Donation]:
        """Получить все пожертвования конкретного пользователя."""
        result = await session.execute(
            select(Donation).where(Donation.user_id == user.id)
        )
        return result.scalars().all()

    async def invest_donation(
        self,
        db_obj: Donation,
        changed: list,
        session: AsyncSession,
    ) -> Donation:
        """Сохранить результаты инвестирования в БД."""
        for obj in changed:
            session.add(obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj


donation_crud = CRUDDonation(Donation)
