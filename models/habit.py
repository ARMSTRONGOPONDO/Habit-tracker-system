from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Habit(Base):
    __tablename__ = 'habit'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(Integer, nullable=False)
    fk_user = Column(Integer, ForeignKey('user.id'), nullable=False)
    fk_habit_type = Column(Integer, ForeignKey('habit_type.id'), nullable=False)

    user = relationship("User")
    habit_type = relationship("HabitType")

    def __repr__(self):
        created_at_formatted = datetime.fromtimestamp(self.created_at).strftime('%d-%m-%Y')
        return f"Habit(id={self.id}, title={self.title}, description={self.description}, created_at={created_at_formatted}, fk_user={self.fk_user}, fk_habit_type={self.fk_habit_type})"
