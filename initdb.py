import sqlite3
from sqlite3 import Error
import random
from datetime import datetime, timedelta

def create_connection():
    """ Create a database connection to a SQLite database """
    conn = None;
    try:
        conn = sqlite3.connect('habits.db') 
        print(sqlite3.version)
    except Error as e:
        print(e)
    if conn:
        return conn
    
def close_connection(conn):
    """ Close a database connection to a SQLite database """
    conn.close()

def create_tables(conn):
    """ Create tables in the database """
    try:
        sql ='''DROP TABLE IF EXISTS habit_tracking;
                DROP TABLE IF EXISTS habit;
                DROP TABLE IF EXISTS habit_type;
                DROP TABLE IF EXISTS user;

                CREATE TABLE user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                );

                CREATE TABLE habit_type (
                    id INTEGER PRIMARY KEY,
                    description TEXT NOT NULL,
                    frequency INTEGER NOT NULL
                );

                CREATE TABLE habit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    created_at INTEGER NOT NULL,
                    fk_user INTEGER NOT NULL,
                    fk_habit_type INTEGER NOT NULL,
                    FOREIGN KEY (fk_user) REFERENCES user(id),
                    FOREIGN KEY (fk_habit_type) REFERENCES habit_type(id)
                );

                CREATE TABLE habit_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fk_habit INTEGER NOT NULL,
                    checked_at INTEGER NOT NULL,
                    FOREIGN KEY (fk_habit) REFERENCES habit(id)
                );'''
        conn.executescript(sql)
    except Error as e:
        print(e)

def populate_tables(conn):
    """ Add admin user, add habit types: daily, weekly, add 6 habits for admin user"""
    try:
        sql = '''INSERT INTO user(email,username,password,created_at)
                 VALUES('admin@gmail.com','admin','admin',strftime('%s','now'));'''
        conn.execute(sql)
        sql = '''INSERT INTO habit_type(id,description,frequency)
                 VALUES(1,'daily',1);'''
        conn.execute(sql)
        sql = '''INSERT INTO habit_type(id,description,frequency)
                 VALUES(2,'weekly',7);'''
        conn.execute(sql)
        sql = '''INSERT INTO habit(title,description,created_at,fk_user,fk_habit_type)
                 VALUES('Drink 1 lt of water','Drink 1 liter of water every day',strftime('%s','now'),1,1);'''
        conn.execute(sql)
        sql = '''INSERT INTO habit(title,description,created_at,fk_user,fk_habit_type)
                 VALUES('Walk 30 minutes','Walk 30 minutes every day',strftime('%s','now'),1,1);'''
        conn.execute(sql)
        sql = '''INSERT INTO habit(title,description,created_at,fk_user,fk_habit_type)
                 VALUES('Read 20 pages','Read 20 pages of a book every day',strftime('%s','now'),1,1);'''
        conn.execute(sql)
        sql = '''INSERT INTO habit(title,description,created_at,fk_user,fk_habit_type)
                 VALUES('Go to the pub','Go to the pub with friends every week',strftime('%s','now'),1,2);'''
        conn.execute(sql)
        sql = '''INSERT INTO habit(title,description,created_at,fk_user,fk_habit_type)
                 VALUES('Swim','Swim every week',strftime('%s','now'),1,2);'''
        conn.execute(sql)
        sql = '''INSERT INTO habit(title,description,created_at,fk_user,fk_habit_type)
                 VALUES('Have a shower','Have a shower every day',strftime('%s','now'),1,1);'''
        conn.execute(sql)
    except Error as e:
        print(e)

def populate_habit_tracking(conn):
    """ Populate randomly the habit_tracking table with 300 rows 
    with dates between 1st of December 2023 and yesterday at maximum 1 row per day per habit """
    try:
        # Calculate the date range
        start_date = datetime(2023, 12, 1)
        end_date = datetime.now() - timedelta(days=1)
        delta = end_date - start_date

        # Get all habits
        cur = conn.cursor()
        cur.execute("SELECT id FROM habit")
        habit_ids = [row[0] for row in cur.fetchall()]

        # Generate random dates and insert data
        inserted_count = 0
        while inserted_count < 300:
            for habit_id in habit_ids:

                random_days = random.randint(0, delta.days)
                random_date = start_date + timedelta(days=random_days)
                timestamp = int(random_date.timestamp())

                # Check if already inserted for this date and habit
                cur.execute("SELECT * FROM habit_tracking WHERE fk_habit = ? AND checked_at = ?", (habit_id, timestamp))
                if cur.fetchone() is None:
                    # Then insert data
                    cur.execute("INSERT INTO habit_tracking (fk_habit, checked_at) VALUES (?, ?)", (habit_id, timestamp))
                    inserted_count += 1
                    if inserted_count >= 300:
                        break

        conn.commit()
    except Error as e:
        print(e)

def init_db():
    """ Create the database, the tables, and populate it with random data """
    print("Initializing database...")
    conn = create_connection()
    with conn:
        create_tables(conn)
        populate_tables(conn)
        populate_habit_tracking(conn)
    close_connection(conn)
    print("Database initialized and populated successfully!")
    print("")