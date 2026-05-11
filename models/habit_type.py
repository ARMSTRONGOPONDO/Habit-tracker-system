from sqlalchemy import Column, Integer, String
from .base import Base

class HabitType(Base):
    __tablename__ = 'habit_type'
    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    frequency = Column(Integer, nullable=False)
