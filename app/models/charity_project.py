from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.core.db import Base


class ProjectDonationBase(Base):
    """Абстрактный базовый класс с общими полями проекта и пожертвования."""

    __abstract__ = True

    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=0, nullable=False)
    fully_invested = Column(Boolean, default=False, nullable=False)
    create_date = Column(DateTime, default=datetime.now, nullable=False)
    close_date = Column(DateTime, nullable=True)


class CharityProject(ProjectDonationBase):
    """Модель целевого проекта."""

    __tablename__ = 'charityproject'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
