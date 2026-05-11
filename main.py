import time
import questionary
from habit_tracking_service import add_new_habit, get_all_habit_by_user_id_and_habit_type_id, get_all_habit_by_user_id_and_unmarked, get_habit_info, get_habit_longest_streak_by_habit_id, get_habits_ordered_by_longest_streak, get_last_month_worst_habit, get_most_long_streak_habit, get_worst_ever_streak_habit, mark_habit_as_done, print_all_habits_by_user_id_and_habit_type_id, print_habit_checked_dates, remove_habit, update_habit

from initdb import init_db


def main():
    """ Entry point of the application """
    
    print_app_logo() # Print the logo
    init_db() # Initialize the database, comment this line if you don't want to reset the database every time you run the application
    user_logged_in = 1 # User id, in this case is the admin user (login mocked)

    while True:
        action = questionary.select(
            "Hi admin, welcome back, what would you like to do today?",
            choices=[
                "Add a new habit",
                "Get habit info",
                "Update a habit",
                "Remove a habit",
                "List of all habits",
                "Mark a habit as done",
                "Longest streak habit",
                "Worst ever streak habit",
                "Last month's worst habit",
                "List of habits with the longest streak",
                "Get longest streak by habit",
                "Quit",
            ],
        ).ask()

        if action == "Add a new habit":
            habit_name = questionary.text("What's the habit name you want to add?").ask()
            habit_description = questionary.text("Insert a short description of the habit.").ask()
            habit_type = questionary.select("What's the habit type?", choices=["Daily", "Weekly"]).ask()
            if habit_type == "Daily":
                habit_type_id = 1
            elif habit_type == "Weekly":
                habit_type_id = 2
            habit_added = add_new_habit(habit_name, habit_description, int(time.time()), user_logged_in, habit_type_id)
            print(f"Habit added: {habit_added}")

        elif action == "Get habit info":
            habit_data = get_all_habit_by_user_id_and_habit_type_id(user_logged_in, None)
            if habit_data:
                choices = [f"{habit_id}. {title}" for habit_id, title in habit_data]
                selected = questionary.select("Which habit do you want to analyze?", choices=choices).ask()
                habit_id = int(selected.split('.')[0])
                print_habit_checked_dates(habit_id) # For check purpose, it prints the checked dates of the habit, comment to disable
                get_habit_info(habit_id)
            else:   
                print("No habits found.")

        elif action == "Update a habit":
            habit_data = get_all_habit_by_user_id_and_habit_type_id(user_logged_in, None)
            if habit_data:
                choices = [f"{habit_id}. {title}" for habit_id, title in habit_data]
                selected = questionary.select("Which habit do you want to update?", choices=choices).ask()
                habit_id = int(selected.split('.')[0])
                habit_name = questionary.text("What's the habit name you want to update?").ask()
                habit_description = questionary.text("Insert a short description of the habit.").ask()
                habit_type = questionary.select("What's the habit type?", choices=["Daily", "Weekly"]).ask()
                if habit_type == "Daily":
                    habit_type_id = 1
                elif habit_type == "Weekly":
                    habit_type_id = 2
                habit_updated = update_habit(habit_id, habit_name, habit_description, habit_type_id)
                print(f"Habit updated with id: {habit_updated}")
            else:
                print("No habits found.")

        elif action == "Remove a habit":
            habit_data = get_all_habit_by_user_id_and_habit_type_id(user_logged_in, None)
            if habit_data:
                choices = [f"{habit_id}. {title}" for habit_id, title in habit_data]
                selected = questionary.select("Which habit do you want to remove?", choices=choices).ask()
                habit_id = int(selected.split('.')[0])  

                remove_habit(habit_id)
                print(f"Habit removed with id: {habit_id}")
                print("Habit list updated:")
                print(print_all_habits_by_user_id_and_habit_type_id(user_logged_in, None))
            else:
                print("No habits found.")

        elif action == "List of all habits":
            habit_type = questionary.select("What's the habit type list you want to see?", choices=["All", "Daily", "Weekly"]).ask()
            habit_type_id = None
            if habit_type == "Daily":
                habit_type_id = 1
            elif habit_type == "Weekly":
                habit_type_id = 2
            list_of_habits = print_all_habits_by_user_id_and_habit_type_id(user_logged_in, habit_type_id)
            print(list_of_habits)

        elif action == "Mark a habit as done":
            list_of_habits_unmarked = get_all_habit_by_user_id_and_unmarked(user_logged_in)
            if list_of_habits_unmarked:
                selected = questionary.select("Which habit do you want to mark as done?", choices=list_of_habits_unmarked).ask()
                habit_id = int(selected.split('.')[0])

                mark_habit_as_done(habit_id)
                print(f"Habit marked as done with id: {habit_id}")
            else:
                print("No unmarked habits found.")

        elif action == "Longest streak habit":
            habit_longer = get_most_long_streak_habit()
            print(f"The habit with the longest streak is: {habit_longer}")

        elif action == "Worst ever streak habit":
            habit_worst = get_worst_ever_streak_habit()
            print(f"The habit with the worst ever streak is: {habit_worst}")

        elif action == "Last month's worst habit":
            last_month_worst_habit = get_last_month_worst_habit()
            print(f"The last month's worst habit is: {last_month_worst_habit}")

        elif action == "List of habits with the longest streak":
            list_of_habits_longest_streak = get_habits_ordered_by_longest_streak(user_logged_in)
            print(list_of_habits_longest_streak)

        elif action == "Get longest streak by habit":
            habit_data = get_all_habit_by_user_id_and_habit_type_id(user_logged_in, None)
            if habit_data:
                choices = [f"{habit_id}. {title}" for habit_id, title in habit_data]
                selected = questionary.select("Which habit do you want to analyze?", choices=choices).ask()
                habit_id = int(selected.split('.')[0])
                habit_longest_streak = get_habit_longest_streak_by_habit_id(habit_id)
                print(habit_longest_streak)
            else:
                print("No habits found.")

        elif action == "Quit":
            break

    print("Bye bye!")

def print_app_logo():
    """ Print the logo of the application and the signature """
    logo = """
██╗  ██╗ █████╗ ██████╗ ██╗████████╗    ████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ 
██║  ██║██╔══██╗██╔══██╗██║╚══██╔══╝    ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
███████║███████║██████╔╝██║   ██║          ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
██╔══██║██╔══██║██╔══██╗██║   ██║          ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██║  ██║██║  ██║██████╔╝██║   ██║          ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝   ╚═╝          ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝"""
    sign = """
  _            ___ _                        _    ___                _               _ _      
 | |__ _  _   / __(_)_____ ____ _ _ _  _ _ (_)  / __|__ _ __ _ __ _(_)__ _ _ _  ___| | |__ _ 
 | '_ \ || | | (_ | / _ \ V / _` | ' \| ' \| | | (__/ _` / _` / _` | / _` | ' \/ -_) | / _` |
 |_.__/\_, |  \___|_\___/\_/\__,_|_||_|_||_|_|  \___\__,_\__, \__, |_\__,_|_||_\___|_|_\__,_|
       |__/                                              |___/|___/                          
    """ 

    print(logo)
    print(sign)

if __name__ == '__main__':
    main()