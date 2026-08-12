from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.charity_project import ProjectDonationBase


class Donation(ProjectDonationBase):
    """Модель пожертвования."""

    __tablename__ = 'donation'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text, nullable=True)
