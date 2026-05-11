import pytest
import time
from habit_tracking_service import add_new_habit, Session, mark_habit_as_done, calculate_streak
from models import Habit, HabitTracking, HabitType, User

def test_add_habit():
    """Test adding a new habit."""
    # We use user_id 1 which is created by init_db
    title = "Test Habit"
    desc = "Test Description"
    # Daily is ID 1
    new_habit = add_new_habit(title, desc, int(time.time()), 1, 1)
    assert new_habit.title == title
    assert new_habit.description == desc

def test_mark_habit_done():
    """Test marking a habit as completed."""
    session = Session()
    habit = session.query(Habit).first()
    session.close()
    
    if habit:
        initial_count = len(session.query(HabitTracking).filter(HabitTracking.fk_habit == habit.id).all())
        mark_habit_as_done(habit.id)
        
        session = Session()
        new_count = len(session.query(HabitTracking).filter(HabitTracking.fk_habit == habit.id).all())
        session.close()
        assert new_count == initial_count + 1

def test_calculate_streak():
    """Test the streak calculation logic."""
    # Create mock tracking data (timestamps 1 day apart)
    t1 = HabitTracking(checked_at=100000)
    t2 = HabitTracking(checked_at=100000 + 86400) # +1 day
    t3 = HabitTracking(checked_at=100000 + 86400 * 2) # +2 days
    
    trackings = [t1, t2, t3]
    streak, start, end = calculate_streak(trackings)
    
    assert streak == 3
    assert start == 100000
    assert end == 100000 + 86400 * 2

def test_calculate_streak_broken():
    """Test streak reset logic."""
    t1 = HabitTracking(checked_at=100000)
    t2 = HabitTracking(checked_at=100000 + 86400 * 2) # Gap of 2 days
    
    trackings = [t1, t2]
    streak, start, end = calculate_streak(trackings)
    
    assert streak == 1
