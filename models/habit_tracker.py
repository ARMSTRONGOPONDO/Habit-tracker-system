import habit_tracking_service as service

class HabitTracker:
    """
    Controller class for habit tracking operations.
    Provides a high-level interface to the habit tracking services.
    """
    def __init__(self, user_id=1):
        self.user_id = user_id

    def get_habits(self, habit_type_id=None):
        return service.get_all_habit_by_user_id_and_habit_type_id(self.user_id, habit_type_id)

    def add_habit(self, title, description, habit_type_id):
        import time
        return service.add_new_habit(title, description, int(time.time()), self.user_id, habit_type_id)

    def mark_done(self, habit_id):
        return service.mark_habit_as_done(habit_id)

    def delete_habit(self, habit_id):
        return service.remove_habit(habit_id)

    def get_streaks(self):
        return service.get_habits_ordered_by_longest_streak(self.user_id)
