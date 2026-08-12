from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.core.yandex_client import YandexDiskClient, get_yandex_client
from app.crud.charity_project import charity_project_crud
from app.services.yandex_api import create_simple_report

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.post(
    '/',
    response_model=str,
    summary='Создать отчёт на Яндекс Диске',
    dependencies=[Depends(current_superuser)],
)
async def create_report(
    session: SessionDep,
    client: YandexDiskClient = Depends(get_yandex_client),
):
    """Создать Excel-отчёт с закрытыми проектами и загрузить на Яндекс Диск."""
    try:
        projects = await charity_project_crud.get_projects_by_completion_rate(
            session
        )
        if not projects:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Нет закрытых проектов для отчёта.',
            )
        return await create_simple_report(client, projects)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f'Ошибка при создании отчёта: {str(e)}',
        )
