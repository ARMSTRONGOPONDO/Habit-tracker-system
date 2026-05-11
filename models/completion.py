from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class HabitTracking(Base):
    __tablename__ = 'habit_tracking'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fk_habit = Column(Integer, ForeignKey('habit.id'), nullable=False)
    checked_at = Column(Integer, nullable=False)

    habit = relationship("Habit")
