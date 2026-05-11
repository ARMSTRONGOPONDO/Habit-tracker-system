import tkinter as tk
from gui.gui import HabitTrackerGUI

def main():
    root = tk.Tk()
    app = HabitTrackerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
