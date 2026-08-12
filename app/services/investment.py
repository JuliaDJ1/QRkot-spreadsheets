from datetime import datetime
from typing import List, Union

from app.models.charity_project import CharityProject
from app.models.donation import Donation


def invest(
    target: Union[CharityProject, Donation],
    sources: List[Union[CharityProject, Donation]],
) -> List[Union[CharityProject, Donation]]:
    """
    Распределить средства из sources в target.

    target  — новый проект или новое пожертвование.
    sources — незакрытые пожертвования (если target — проект)
              или незакрытые проекты (если target — пожертвование).

    Возвращает список изменённых объектов для сохранения в БД.
    """
    changed = []
    remaining_target = target.full_amount - (target.invested_amount or 0)

    for source in sources:
        remaining_source = source.full_amount - (source.invested_amount or 0)
        amount = min(remaining_target, remaining_source)

        source.invested_amount = (source.invested_amount or 0) + amount
        if source.invested_amount >= source.full_amount:
            source.fully_invested = True
            source.close_date = datetime.now()
        changed.append(source)

        target.invested_amount = (target.invested_amount or 0) + amount
        remaining_target -= amount

        if remaining_target == 0:
            target.fully_invested = True
            target.close_date = datetime.now()
            break

    return changed
