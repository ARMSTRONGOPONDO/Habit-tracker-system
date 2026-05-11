import datetime
import time
from matplotlib import pyplot as plt
from sqlalchemy.orm import sessionmaker
from prettytable import PrettyTable
from sqlalchemy import create_engine
from models import Habit, HabitTracking, HabitType

engine = create_engine('sqlite:///habits.db')
Session = sessionmaker(bind=engine)

def get_all_habit_by_user_id_and_habit_type_id(user_id, habit_type_id):
    """ Get all habits by user id and habit type id 
    
    Args:
        user_id (int): The user id
        habit_type_id (int): The habit type id
    Returns:
        list: A list of tuples containing the habit id and title

    """
    session = Session()
    try:
        query = session.query(Habit, HabitType.description).join(HabitType)
        if habit_type_id is not None:
            query = query.filter(Habit.fk_user == user_id, Habit.fk_habit_type == habit_type_id)
        else:
            query = query.filter(Habit.fk_user == user_id)

        habits = query.all()

        return [(habit.id, habit.title) for habit, _ in habits]
    
    except Exception as e:
        print(f"An error occurred while get_all_habit_by_user_id_and_habit_type_id: {e}")
    finally:
        session.close()

def print_all_habits_by_user_id_and_habit_type_id(user_id, habit_type_id):
    """ Print table of all habits by user id and habit type id 
    
    Args:
        user_id (int): The user id
        habit_type_id (int): The habit type id
    Returns:
        PrettyTable: A table containing the habit information
        
    """
    session = Session()
    try:
        query = session.query(Habit, HabitType.description).join(HabitType)
        if habit_type_id is not None:
            query = query.filter(Habit.fk_user == user_id, Habit.fk_habit_type == habit_type_id)
        else:
            query = query.filter(Habit.fk_user == user_id)

        habits = query.all()

        table = PrettyTable()
        table.field_names = ["Habit ID", "Title", "Habit Description", "Created At", "User ID", "Habit Type Description"]
        for habit, habit_type_description in habits:
            created_at_formatted = datetime.datetime.fromtimestamp(habit.created_at).strftime('%Y-%m-%d %H:%M:%S')
            table.add_row([habit.id, habit.title, habit.description, created_at_formatted, habit.fk_user, habit_type_description])

        return table
    except Exception as e:
        print(f"An error occurred while print_all_habits_by_user_id_and_habit_type_id: {e}")
    finally:
        session.close()

def add_new_habit(title, description, created_at, fk_user, fk_habit_type):
    """ Add a new habit to the database 
    
    Args:
        title (str): The title of the habit
        description (str): The description of the habit
        created_at (int): The timestamp when the habit was created
        fk_user (int): The user id
        fk_habit_type (int): The habit type id
        
    Returns:
        Habit: The newly created habit
    
    """
    session = Session()
    try:
        new_habit = Habit(title=title, description=description, created_at=created_at, fk_user=fk_user, fk_habit_type=fk_habit_type)
        session.add(new_habit)
        session.commit()
        session.refresh(new_habit)
        return new_habit
    except Exception as e:
        print(f"An error occurred while add_new_habit: {e}")
        session.rollback()
    finally:
        session.close()

def get_habit_info(habit_id):
    """ Get the habit information showing the habit tracking data in a plot
    
    Args:
        habit_id (int): The habit id
        
    """
    session = Session()
    habit_trackings = session.query(HabitTracking).filter(HabitTracking.fk_habit == habit_id).order_by(HabitTracking.checked_at).all()
    session.close()

    if not habit_trackings:
        print("No tracking data available for this habit.")
        return

    # Date range of the habit tracking
    start_date = datetime.datetime.fromtimestamp(habit_trackings[0].checked_at).date()
    end_date = datetime.datetime.fromtimestamp(habit_trackings[-1].checked_at).date()
    delta = end_date - start_date

    # Create a list of all the dates in the range
    date_list = [start_date + datetime.timedelta(days=i) for i in range(delta.days + 1)]
    completion_status = [0] * len(date_list)  # Initialize the list with 0s

    # Mark the dates when the habit was checked
    for tracking in habit_trackings:
        checked_date = datetime.datetime.fromtimestamp(tracking.checked_at).date()
        index = (checked_date - start_date).days
        completion_status[index] = 1  # Mark the date as checked

    # Plot the data
    plt.figure(figsize=(12, 6))
    plt.bar(date_list, completion_status, color='black')
    plt.title(f'Habit status for ID: {habit_id}')
    plt.xlabel('Date')
    plt.ylabel('Checked (1) - Not Checked (0)')
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.tight_layout()
    plt.show()


def print_habit_checked_dates(habit_id):
    """ (For check purpose of the plot) Print a table of all the days when the selected habit was checked 
    
    Args:
        habit_id (int): The habit id

    """
    session = Session()
    try:
        habit_trackings = session.query(HabitTracking).filter(HabitTracking.fk_habit == habit_id).order_by(HabitTracking.checked_at).all()

        table = PrettyTable()
        table.field_names = ["Checked Date"]

        for tracking in habit_trackings:
            checked_date = datetime.datetime.fromtimestamp(tracking.checked_at).strftime('%Y-%m-%d')
            table.add_row([checked_date])

        print(table)
    except Exception as e:
        print(f"An error occurred while print_habit_checked_dates: {e}")
    finally:
        session.close()


def update_habit(habit_id, title=None, description=None, fk_habit_type=None):
    """ Update a habit 
    
    Args:
        habit_id (int): The habit id
        title (str): The title of the habit
        description (str): The description of the habit
        fk_habit_type (int): The habit type id
        
    Returns:
        Habit: The updated habit
        
    """
    session = Session()
    try:
        habit = session.query(Habit).filter(Habit.id == habit_id).first()
        if habit:
            if title:
                habit.title = title
            if description:
                habit.description = description
            if fk_habit_type:
                habit.fk_habit_type = fk_habit_type
            session.commit()
            session.refresh(habit)
        return habit
    except Exception as e:
        print(f"An error occurred while update_habit: {e}")
        session.rollback()
    finally:
        session.close()

def remove_habit(habit_id):
    """ Remove a habit 
    
    Args:
        habit_id (int): The habit id
        
    """
    session = Session()
    try:
        habit = session.query(Habit).filter(Habit.id == habit_id).first()
        if habit:
            session.delete(habit)
            session.commit()
    except Exception as e:
        print(f"An error occurred while remove_habit: {e}")
        session.rollback()
    finally:
        session.close()

def get_all_habit_by_user_id_and_unmarked(user_id):
    """ Get all habits by user id and unmarked 
    
    Args:
        user_id (int): The user id
        
    Returns:
        list: A list of unmarked habits
        
    """
    session = Session()
    try:
        today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_end = datetime.datetime.combine(datetime.date.today(), datetime.time.max)

        today_start_ts = int(time.mktime(today_start.timetuple()))
        today_end_ts = int(time.mktime(today_end.timetuple()))

        unmarked_habits = session.query(Habit).outerjoin(
            HabitTracking, (Habit.id == HabitTracking.fk_habit) & 
            (HabitTracking.checked_at >= today_start_ts) & 
            (HabitTracking.checked_at <= today_end_ts)
        ).filter(Habit.fk_user == user_id, HabitTracking.id.is_(None)).all()

        result = []
        for habit in unmarked_habits:
            result.append(f"{habit.id}. {habit.title}")

        return result
    except Exception as e:
        print(f"An error occurred while get_all_habit_by_user_id_and_unmarked: {e}")
    finally:
        session.close()


def mark_habit_as_done(habit_id):
    """ Mark a habit as done 
    
    Args:
        habit_id (int): The habit id

    """
    session = Session()
    try:
        new_habit_tracking = HabitTracking(fk_habit=habit_id, checked_at=int(time.time()))
        session.add(new_habit_tracking)
        session.commit()
        session.refresh(new_habit_tracking)
    except Exception as e:
        print(f"An error occurred while mark_habit_as_done: {e}")
        session.rollback()
    finally:
        session.close()

def get_most_long_streak_habit():
    """ Get the habit with the longest streak 
    
    Args:
        user_id (int): The user id
        
    Returns:
        Habit: The habit with the longest streak

    """
    session = Session()
    try:
        max_streak = 0
        max_streak_habit = None
        current_time = int(time.time())

        habits = session.query(Habit).all()
        for habit in habits:
            habit_streaks = session.query(HabitTracking).filter(HabitTracking.fk_habit == habit.id, HabitTracking.checked_at <= current_time).all()
            streak = len(habit_streaks)

            if streak > max_streak:
                max_streak = streak
                max_streak_habit = habit

        return max_streak_habit
    except Exception as e:
        print(f"An error occurred while get_most_long_streak_habit: {e}")
    finally:
        session.close()

def get_worst_ever_streak_habit():
    """ Get the habit with the worst ever streak 
    
    Args:
        user_id (int): The user id
        
    Returns:
        Habit: The habit with the worst ever streak
        
    """
    session = Session()
    try:
        min_streak = float('inf')
        min_streak_habit = None
        current_time = int(time.time())

        habits = session.query(Habit).all()
        for habit in habits:
            habit_streaks = session.query(HabitTracking).filter(HabitTracking.fk_habit == habit.id, HabitTracking.checked_at <= current_time).all()
            streak = len(habit_streaks)

            if streak < min_streak:
                min_streak = streak
                min_streak_habit = habit

        return min_streak_habit
    except Exception as e:
        print(f"An error occurred while get_worst_ever_streak_habit: {e}")
    finally:
        session.close()

def get_last_month_worst_habit():
    """ Get the worst habit from the last month 
    
    Args:
        user_id (int): The user id

    Returns:
        Habit: The habit with the worst streak from the last month

    """
    session = Session()
    try:
        min_streak = float('inf')
        min_streak_habit = None
        one_month_ago = int(time.time()) - 30 * 24 * 60 * 60

        habits = session.query(Habit).all()
        for habit in habits:
            habit_streaks = session.query(HabitTracking).filter(HabitTracking.fk_habit == habit.id, HabitTracking.checked_at >= one_month_ago).all()
            streak = len(habit_streaks)

            if streak < min_streak:
                min_streak = streak
                min_streak_habit = habit

        return min_streak_habit
    except Exception as e:
        print(f"An error occurred while get_last_month_worst_habit: {e}")
    finally:
        session.close()

def calculate_streak(habit_trackings):
    """ Calculate the longest streak and its date range for a habit. 
    
    Args:
        habit_trackings (list): A list of habit tracking objects

    Returns:
        tuple: A tuple containing the longest streak, the start date and the end date

    """
    if not habit_trackings:
        return 0, None, None

    longest_streak = current_streak = 1
    longest_start = longest_end = current_start = habit_trackings[0].checked_at
    previous_day = current_start

    for tracking in habit_trackings[1:]:
        if tracking.checked_at - previous_day == 86400:  # 86400 seconds in a day
            current_streak += 1
            if current_streak > longest_streak:
                longest_streak = current_streak
                longest_start = current_start
                longest_end = tracking.checked_at
        else:
            current_streak = 1
            current_start = tracking.checked_at

        previous_day = tracking.checked_at

    return longest_streak, longest_start, longest_end

def get_habits_ordered_by_longest_streak(user_id):
    """ Get all habits by user_id ordered by the longest streak. 
    
    Args:
        user_id (int): The user id
        
    Returns:
        PrettyTable: A table containing the habit information ordered by the longest streak
        
    """
    session = Session()
    try:
        habits = session.query(Habit).filter(Habit.fk_user == user_id).all()
        habit_streaks = []

        for habit in habits:
            habit_trackings = session.query(HabitTracking).filter(HabitTracking.fk_habit == habit.id).order_by(HabitTracking.checked_at).all()
            streak_length, start_date, end_date = calculate_streak(habit_trackings)

            habit_streaks.append((habit, streak_length, start_date, end_date))

        habit_streaks.sort(key=lambda x: x[1], reverse=True)

        table = PrettyTable()
        table.field_names = ["Habit ID", "Title", "Longest Streak", "Streak Start Date", "Streak End Date"]

        for habit, streak, start, end in habit_streaks:
            start_date_str = datetime.datetime.fromtimestamp(start).strftime('%Y-%m-%d') if start else 'N/A'
            end_date_str = datetime.datetime.fromtimestamp(end).strftime('%Y-%m-%d') if end else 'N/A'
            table.add_row([habit.id, habit.title, streak, start_date_str, end_date_str])

        return table
    except Exception as e:
        print(f"An error occurred while get_habits_ordered_by_longest_streak: {e}")
    finally:
        session.close()

def get_habit_longest_streak_by_habit_id(habit_id):
    """ Get the longest streak for a habit by habit id 
    
    Args:
        habit_id (int): The habit id
        
    Returns:
        PrettyTable: A table containing the habit information "Habit ID", "Title", "Longest Streak", "Streak Start Date", "Streak End Date"
    
    """
    session = Session()
    try:
        habit = session.query(Habit).filter(Habit.id == habit_id).first()
        habit_trackings = session.query(HabitTracking).filter(HabitTracking.fk_habit == habit_id).order_by(HabitTracking.checked_at).all()
        streak_length, start_date, end_date = calculate_streak(habit_trackings)

        table = PrettyTable()
        table.field_names = ["Habit ID", "Title", "Longest Streak", "Streak Start Date", "Streak End Date"]
        start_date_str = datetime.datetime.fromtimestamp(start_date).strftime('%Y-%m-%d') if start_date else 'N/A'
        end_date_str = datetime.datetime.fromtimestamp(end_date).strftime('%Y-%m-%d') if end_date else 'N/A'
        table.add_row([habit.id, habit.title, streak_length, start_date_str, end_date_str])

        return table
    except Exception as e:
        print(f"An error occurred while get_habit_longest_streak_by_habit_id: {e}")
    finally:
        session.close()