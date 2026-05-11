from datetime import datetime

def get_all_habits(cursor):
    """
    Fetch all habits from the database.

    Args:
        cursor (sqlite3.Cursor): The database cursor.

    Returns:
        list: A list of habit records.
    """
    cursor.execute("SELECT * FROM habits;")
    return cursor.fetchall()

def filter_by_period(cursor, periodicity):
    """
    Fetch habits filtered by periodicity (Daily/Weekly).

    Args:
        cursor (sqlite3.Cursor): The database cursor.
        periodicity (str): The periodicity filter ("Daily" or "Weekly").

    Returns:
        list: A list of filtered habit records.
    """
    cursor.execute("SELECT * FROM habits WHERE periodicity = ?;", (periodicity,))
    return cursor.fetchall()

def longest_streak_for(habit_id, cursor):
    """
    Calculate the longest streak for a specific habit.

    Args:
        habit_id (int): The unique ID of the habit.
        cursor (sqlite3.Cursor): The database cursor.

    Returns:
        int: The longest streak of consecutive completions.
    """
    cursor.execute(
        "SELECT completed_at FROM completions WHERE habit_id = ? ORDER BY completed_at ASC;",
        (habit_id,)
    )
    completions = [
        datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in cursor.fetchall()
    ]
    return compute_streak(completions)

def longest_streak_all(cursor):
    """
    Calculate the longest streak for all habits in the database.

    Args:
        cursor (sqlite3.Cursor): The database cursor.

    Returns:
        list: A list of tuples containing habit IDs and their longest streaks.
    """
    cursor.execute("SELECT id FROM habits;")
    habit_ids = [row[0] for row in cursor.fetchall()]

    # Calculate and collect streaks for each habit
    streaks = []
    for habit_id in habit_ids:
        streak = longest_streak_for(habit_id, cursor)
        streaks.append((habit_id, streak))

    return streaks

def compute_streak(completions):
    """
    Compute the longest streak from a list of completion timestamps.

    Args:
        completions (list): A list of datetime objects representing completions.

    Returns:
        int: The longest streak of consecutive completions.
    """
    # Edge case: no completions
    if not completions:
        return 0

    # Initialize streak counters
    longest_streak = current_streak = 1

    for i in range(1, len(completions)):
        delta = completions[i] - completions[i - 1]
        # Check if the completions are consecutive (1 day apart)
        if delta.days <= 1:
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
        else:
            current_streak = 1  # Reset current streak on a gap

    return longest_streak