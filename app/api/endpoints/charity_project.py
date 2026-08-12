from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.investment import invest

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    summary='Показать список всех целевых проектов',
)
async def get_all_charity_projects(session: SessionDep):
    """Доступно всем пользователям."""
    return await charity_project_crud.get_multi(session)


@router.post(
    '/',
    response_model=CharityProjectDB,
    summary='Создать целевой проект',
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
    project_in: CharityProjectCreate,
    session: SessionDep,
):
    """Только для суперпользователя."""
    project_id = await charity_project_crud.get_project_id_by_name(
        project_in.name, session
    )
    if project_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!',
        )

    new_project = await charity_project_crud.create(project_in, session)
    free_donations = await donation_crud.get_not_fully_invested(session)
    changed = invest(new_project, free_donations)
    return await charity_project_crud.invest_project(
        new_project, changed, session
    )


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    summary='Редактировать целевой проект',
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: SessionDep,
):
    """Только для суперпользователя."""
    project = await charity_project_crud.get(project_id, session)
    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден!',
        )

    if project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!',
        )

    if obj_in.name is not None and obj_in.name != project.name:
        existing_id = await charity_project_crud.get_project_id_by_name(
            obj_in.name, session
        )
        if existing_id is not None:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Проект с таким именем уже существует!',
            )

    if obj_in.full_amount is not None:
        if obj_in.full_amount < project.invested_amount:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=(
                    'Нелья установить значение full_amount '
                    'меньше уже вложенной суммы.'
                ),
            )

    project = await charity_project_crud.update(project, obj_in, session)

    if project.full_amount == project.invested_amount:
        if project.invested_amount > 0:
            project = await charity_project_crud.close_project(
                project, session
            )

    return project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    summary='Удалить целевой проект',
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
    project_id: int,
    session: SessionDep,
):
    """Только для суперпользователя."""
    project = await charity_project_crud.get(project_id, session)
    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден!',
        )

    if project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!',
        )

    return await charity_project_crud.remove(project, session)
