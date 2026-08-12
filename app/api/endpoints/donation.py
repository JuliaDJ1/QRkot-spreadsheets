from typing import Annotated, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models.user import User
from app.schemas.donation import DonationCreate, DonationFullInfoDB
from app.services.investment import invest

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


def _serialize_donation(donation) -> Dict:
    """Сериализовать пожертвование, включая comment только если он есть."""
    result = {
        'id': donation.id,
        'full_amount': donation.full_amount,
        'create_date': donation.create_date.isoformat(),
    }
    if donation.comment is not None:
        result['comment'] = donation.comment
    return result


@router.get(
    '/',
    response_model=List[DonationFullInfoDB],
    summary='Показать список всех пожертвований',
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(session: SessionDep):
    """Только для суперпользователя."""
    return await donation_crud.get_multi(session)


@router.get(
    '/my',
    summary='Показать мои пожертвования',
)
async def get_my_donations(
    session: SessionDep,
    user: User = Depends(current_user),
):
    """Для зарегистрированного пользователя — его пожертвования."""
    donations = await donation_crud.get_by_user(user, session)
    return [_serialize_donation(d) for d in donations]


@router.post(
    '/',
    summary='Создать пожертвование',
)
async def create_donation(
    donation_in: DonationCreate,
    session: SessionDep,
    user: User = Depends(current_user),
):
    """Для зарегистрированного пользователя."""
    new_donation = await donation_crud.create(donation_in, session)
    new_donation.user_id = user.id
    open_projects = await charity_project_crud.get_not_fully_invested(session)
    changed = invest(new_donation, open_projects)
    result = await donation_crud.invest_donation(
        new_donation, changed, session
    )
    return _serialize_donation(result)
