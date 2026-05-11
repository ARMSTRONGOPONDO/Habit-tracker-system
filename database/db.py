import sqlite3

class Database:
    def __init__(self, db_name="habit_tracker.db"):
        self.connection = sqlite3.connect(db_name)
        self.init_schema()

    def init_schema(self):
        cursor = self.connection.cursor()
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                periodicity TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                completed_at TEXT NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
            );
            """
        )
        self.connection.commit()

    def seed_data(self):
        cursor = self.connection.cursor()
        habits = [
            ("Morning Exercise", "30+ minutes of physical activity", "Daily", "2026-05-01"),
            ("Mindful Check-in", "5 minutes of journaling or meditation", "Daily", "2026-05-01"),
            ("Deep Work Block", "90 minutes of distraction-free work", "Daily", "2026-05-01"),
            ("Weekly Life Review", "Review past-week goals and plan ahead", "Weekly", "2026-05-01"),
            ("Social Connection", "Meaningful interaction with a friend or family", "Weekly", "2026-05-01")
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO habits (name, description, periodicity, created_at) VALUES (?, ?, ?, ?);",
            habits
        )
        self.connection.commit()

    def close(self):
        self.connection.close()