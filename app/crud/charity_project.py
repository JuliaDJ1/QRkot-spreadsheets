from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase[CharityProject]):
    """CRUD-операции для целевых проектов."""

    async def get_project_id_by_name(
        self,
        project_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        """Найти проект по имени и вернуть его id или None."""
        result = await session.execute(
            select(CharityProject).where(
                CharityProject.name == project_name
            )
        )
        db_project = result.scalars().first()
        return db_project.id if db_project else None

    async def get_not_fully_invested(
        self,
        session: AsyncSession,
    ) -> List[CharityProject]:
        """Получить открытые проекты, отсортированные по дате создания."""
        result = await session.execute(
            select(CharityProject)
            .where(CharityProject.fully_invested.is_(False))
            .order_by(CharityProject.create_date)
        )
        return result.scalars().all()

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession,
    ) -> List[CharityProject]:
        """Получить закрытые проекты, отсортированные по скорости сбора."""
        result = await session.execute(
            select(CharityProject)
            .where(CharityProject.fully_invested.is_(True))
            .order_by(
                CharityProject.close_date - CharityProject.create_date
            )
        )
        return result.scalars().all()

    async def close_project(
        self,
        db_obj: CharityProject,
        session: AsyncSession,
    ) -> CharityProject:
        """Закрыть проект: выставить fully_invested и close_date."""
        db_obj.fully_invested = True
        db_obj.close_date = datetime.now()
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def invest_project(
        self,
        db_obj: CharityProject,
        changed: list,
        session: AsyncSession,
    ) -> CharityProject:
        """Сохранить результаты инвестирования в БД."""
        for obj in changed:
            session.add(obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj


charity_project_crud = CRUDCharityProject(CharityProject)
