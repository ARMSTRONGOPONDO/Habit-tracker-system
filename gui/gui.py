import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import habit_tracking_service as service
import time
from initdb import init_db
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from models import User

class HabitTrackerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Habit Tracker Pro")
        self.master.geometry("1000x700")
        
        # Styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
        self.style.configure("Info.TLabel", font=("Helvetica", 10))
        
        # Initialize database if it doesn't exist
        if not os.path.exists('habits.db'):
            init_db()
        
        self.current_user = None
        self.habits = []
        
        self.main_container = None
        self.show_login_screen()

    def show_login_screen(self):
        """Displays the login screen."""
        if self.main_container:
            self.main_container.destroy()
            
        self.login_frame = ttk.Frame(self.master, padding="20")
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        ttk.Label(self.login_frame, text="Habit Tracker Login", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
        
        ttk.Label(self.login_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(self.login_frame, width=30)
        self.username_entry.grid(row=1, column=1, pady=5)
        self.username_entry.insert(0, "admin") # Convenience for testing
        
        ttk.Label(self.login_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*", width=30)
        self.password_entry.grid(row=2, column=1, pady=5)
        self.password_entry.insert(0, "admin") # Convenience for testing
        
        login_btn = ttk.Button(self.login_frame, text="Login", command=self.handle_login)
        login_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Bind Enter key
        self.master.bind('<Return>', lambda e: self.handle_login())

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        session = service.Session()
        user = session.query(User).filter(User.username == username, User.password == password).first()
        session.close()
        
        if user:
            self.current_user = user
            self.login_frame.destroy()
            self.master.unbind('<Return>')
            self.setup_main_ui()
            self.refresh_habits()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def handle_logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.current_user = None
            self.main_container.destroy()
            self.show_login_screen()

    def setup_main_ui(self):
        # Main Container
        self.main_container = ttk.Frame(self.master)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Top Bar: User Info & Logout
        top_bar = ttk.Frame(self.main_container, padding="10", relief="raised")
        top_bar.pack(fill=tk.X)
        
        user_name = self.current_user.username
        user_email = self.current_user.email
        ttk.Label(top_bar, text=f"Welcome, {user_name} ({user_email})", style="Header.TLabel").pack(side=tk.LEFT)
        
        ttk.Button(top_bar, text="Logout", command=self.handle_logout).pack(side=tk.RIGHT)
        
        # Dashboard Content
        content_frame = ttk.Frame(self.main_container, padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left Column: Habit List and Controls
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(left_frame, text="Your Habits", font=("Helvetica", 12, "bold")).pack(pady=(0, 5))
        
        self.habit_listbox = tk.Listbox(left_frame, width=35, height=15, font=("Helvetica", 10))
        self.habit_listbox.pack(fill=tk.BOTH, expand=True)
        self.habit_listbox.bind('<<ListboxSelect>>', self.on_habit_select)

        # Habit Action Buttons
        btn_grid = ttk.Frame(left_frame)
        btn_grid.pack(fill=tk.X, pady=10)

        ttk.Button(btn_grid, text="Add", command=self.show_add_dialog).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ttk.Button(btn_grid, text="Edit", command=self.show_edit_dialog).grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        ttk.Button(btn_grid, text="Done!", command=self.on_check_off).grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        ttk.Button(btn_grid, text="Delete", command=self.on_delete_habit).grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        
        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)

        # Right Column: Dashboard and Charts
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Habit Info Panel
        self.info_frame = ttk.LabelFrame(right_frame, text="Habit Details", padding=10)
        self.info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.details_label = ttk.Label(self.info_frame, text="Select a habit to see details", style="Info.TLabel", wraplength=500)
        self.details_label.pack(fill=tk.X)

        # Analytics Buttons
        ana_btn_frame = ttk.Frame(right_frame)
        ana_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(ana_btn_frame, text="Global Streaks", command=self.show_analytics).pack(side=tk.LEFT, padx=5)
        ttk.Button(ana_btn_frame, text="Month's Worst", command=self.show_worst_habit).pack(side=tk.LEFT, padx=5)
        ttk.Button(ana_btn_frame, text="Refresh All", command=self.refresh_habits).pack(side=tk.RIGHT, padx=5)

        # Chart Area
        self.chart_frame = ttk.LabelFrame(right_frame, text="Progress Visualization", padding=10)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
        
        self.fig, self.ax = plt.subplots(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def refresh_habits(self):
        """Update the list of habits in the listbox."""
        if not self.current_user: return
        self.habit_listbox.delete(0, tk.END)
        self.habits = service.get_all_habit_by_user_id_and_habit_type_id(self.current_user.id, None)
        
        if self.habits:
            for habit_id, title in self.habits:
                self.habit_listbox.insert(tk.END, f" {title}")
        else:
            self.habit_listbox.insert(tk.END, " No habits found.")

    def on_habit_select(self, event):
        selection = self.habit_listbox.curselection()
        if not selection or not self.habits:
            return
        
        index = selection[0]
        if index >= len(self.habits):
            return
            
        habit_id, title = self.habits[index]
        self.display_habit_details(habit_id)
        self.update_chart(habit_id, title)

    def display_habit_details(self, habit_id):
        # Fetch habit details including type
        from models import Habit, HabitType
        session = service.Session()
        habit = session.query(Habit).filter(Habit.id == habit_id).first()
        h_type = session.query(HabitType).filter(HabitType.id == habit.fk_habit_type).first()
        session.close()

        if habit:
            created_at = datetime.datetime.fromtimestamp(habit.created_at).strftime('%Y-%m-%d')
            periodicity = h_type.description if h_type else "Unknown"
            details = (f"Title: {habit.title}\n"
                       f"Description: {habit.description or 'No description'}\n"
                       f"Periodicity: {periodicity.capitalize()}\n"
                       f"Created on: {created_at}")
            self.details_label.config(text=details)

    def update_chart(self, habit_id, title):
        self.ax.clear()
        
        # Fetch tracking data
        from models import HabitTracking
        session = service.Session()
        trackings = session.query(HabitTracking).filter(HabitTracking.fk_habit == habit_id).order_by(HabitTracking.checked_at).all()
        session.close()

        if not trackings:
            self.ax.text(0.5, 0.5, "No tracking data yet", ha='center', va='center')
        else:
            # Show last 30 days
            end_date = datetime.datetime.now().date()
            plot_start = end_date - datetime.timedelta(days=29)
            
            date_list = [plot_start + datetime.timedelta(days=i) for i in range(30)]
            status = [0] * 30
            
            check_dates = {datetime.datetime.fromtimestamp(t.checked_at).date() for t in trackings}
            for i, d in enumerate(date_list):
                if d in check_dates:
                    status[i] = 1

            self.ax.bar(date_list, status, color='#2ecc71')
            self.ax.set_title(f"30-Day Activity: {title}")
            self.ax.set_ylim(0, 1.2)
            self.ax.set_yticks([0, 1])
            self.ax.set_yticklabels(['Missed', 'Done'])
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')

        self.fig.tight_layout()
        self.canvas.draw()

    def show_add_dialog(self):
        name = simpledialog.askstring("Add Habit", "Enter habit name:")
        if not name: return
        
        description = simpledialog.askstring("Add Habit", "Enter habit description:")
        type_choice = simpledialog.askstring("Add Habit", "Periodicity (Daily/Weekly):")
        
        type_id = 2 if type_choice and type_choice.lower() == "weekly" else 1
        service.add_new_habit(name, description, int(time.time()), self.current_user.id, type_id)
        self.refresh_habits()

    def show_edit_dialog(self):
        selection = self.habit_listbox.curselection()
        if not selection or not self.habits: return
        
        habit_id, old_title = self.habits[selection[0]]
        
        new_name = simpledialog.askstring("Edit Habit", f"Update name for '{old_title}':", initialvalue=old_title)
        if not new_name: return
        
        new_desc = simpledialog.askstring("Edit Habit", "Update description:")
        new_type = simpledialog.askstring("Edit Habit", "Update periodicity (Daily/Weekly):")
        
        type_id = 2 if new_type and new_type.lower() == "weekly" else 1
        service.update_habit(habit_id, new_name, new_desc, type_id)
        self.refresh_habits()
        self.on_habit_select(None)

    def on_check_off(self):
        selection = self.habit_listbox.curselection()
        if not selection or not self.habits:
            messagebox.showwarning("Warning", "Select a habit first!")
            return
        
        habit_id, title = self.habits[selection[0]]
        service.mark_habit_as_done(habit_id)
        messagebox.showinfo("Success", f"'{title}' checked off!")
        self.on_habit_select(None) 

    def on_delete_habit(self):
        selection = self.habit_listbox.curselection()
        if not selection or not self.habits: return
        
        habit_id, title = self.habits[selection[0]]
        if messagebox.askyesno("Confirm Delete", f"Delete habit '{title}'?"):
            service.remove_habit(habit_id)
            self.refresh_habits()
            self.details_label.config(text="Select a habit to see details")
            self.ax.clear()
            self.canvas.draw()

    def show_analytics(self):
        table = service.get_habits_ordered_by_longest_streak(self.current_user.id)
        win = tk.Toplevel(self.master)
        win.title("Longest Streaks")
        txt = tk.Text(win, height=15, width=90, font=("Courier", 10))
        txt.insert(tk.END, str(table))
        txt.config(state=tk.DISABLED)
        txt.pack(padx=20, pady=20)

    def show_worst_habit(self):
        h = service.get_last_month_worst_habit()
        if h:
            messagebox.showinfo("Worst Habit", f"'{h.title}' is struggling this month.")
        else:
            messagebox.showinfo("Info", "No data for last month.")

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTrackerGUI(root)
    root.mainloop()
