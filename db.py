import sqlite3

from OOP import Habit


# This is where we define the name of the database. This database will be called user_data.
# The database will be created if it does not exist, and connected to if it does exist.
def get_db(name="user_database_information.db"):
    db = sqlite3.connect(name)
    db.execute("PRAGMA foreign_keys = ON;")  # This will allow us to use foreign keys
    return db


# here we define a cursor so that we can create tables. We will be creating the user table first.
def create_table_for_users(db):
    cur = db.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id     INTEGER PRIMARY KEY,
            user_name   TEXT NOT NULL
        );
    """)


# here we create the habit table with all its properties.
def create_table_for_habits(db):
    cur = db.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Habits (
            habit_id             INTEGER PRIMARY KEY,
            user_id              INTEGER NOT NULL,
            habit_name           TEXT    NOT NULL,

            frequency            TEXT    NOT NULL
                                      CHECK (frequency IN ('daily','weekly')),

            start_date           TEXT    NOT NULL,  -- 'YYYY-MM-DD'
            start_time           TEXT,              -- 'HH:MM'
            check_date           TEXT,              -- 'YYYY-MM-DD'
            check_time           TEXT,              -- 'HH:MM'

            longest_streak       INTEGER NOT NULL DEFAULT 0 CHECK (longest_streak >= 0),
            current_streak       INTEGER NOT NULL DEFAULT 0 CHECK (current_streak >= 0),
            failed_attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (failed_attempt_count >= 0),

            FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
            UNIQUE (user_id, habit_name)
        );
    """)


# here we will insert new users to the user table.
def insert_user(cur, user_name, user_id=None):

    # If user_ID is None, SQLite will auto-assign.
    if user_id is None:
        cur.execute("INSERT INTO Users (user_name) VALUES (?)", (user_name,))
        return cur.lastrowid
    else:
        cur.execute("INSERT INTO Users (user_ID, user_name) VALUES (?, ?)", (user_id, user_name))
        return user_id


# Here we will insert a new habit for a user. The following shows all the properties without the use of a habit class.
# def insert_habit(cur, user_ID, habit_name, frequency, start_date, start_time, check_date, check_time, habit_ID=None)
def insert_habit(cur, user_id, habit: Habit, habit_id=None):
    cols = ["user_id", "habit_name", "frequency", "start_date", "start_time", "check_date", "check_time"]
    vals = [user_id, habit.habit_name, habit.frequency, habit.created_date, habit.created_time, habit.check_date,
            habit.check_time]

    if habit_id is None:
        cur.execute(f"""
                INSERT INTO Habits ({", ".join(cols)})
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, tuple(vals))
        return cur.lastrowid
    else:
        cols = ["habit_id"] + cols
        vals = [habit_id] + vals
        placeholders = ", ".join(["?"] * len(vals))
        cur.execute(f"""
                INSERT INTO Habits ({", ".join(cols)})
                VALUES ({placeholders})
            """, tuple(vals))
        return habit_id


# A habit will be mark successful.
def mark_habit_success(cur, habit_id):

    # increment current_streak and increment longest_streak if needed
    cur.execute("""
        UPDATE Habits
        SET current_streak = current_streak + 1,
            longest_streak = CASE
                                WHEN current_streak + 1 > longest_streak
                                THEN current_streak + 1
                                ELSE longest_streak
                             END
        WHERE habit_id = ?;
    """, (habit_id,))

    # shift next_check_date based on frequency
    cur.execute("""
        UPDATE Habits
        SET check_date = date(
            COALESCE(check_date, date('now')),
            CASE frequency
              WHEN 'daily'   THEN '+1 day'
              WHEN 'weekly'  THEN '+7 day'


            END
        )
        WHERE habit_id = ?;
    """, (habit_id,))


def mark_habit_fail(cur, habit_id):

    # Reset current_streak and increment failed_attempt_count. Also create a new start date.
    cur.execute("""
        UPDATE Habits
        SET current_streak = 0,
            failed_attempt_count = failed_attempt_count + 1,
            check_date = date('now', '+1 day'),
            start_date = date('now')
        WHERE habit_id = ?;
    """, (habit_id,))


# A user's data will be gathered using their unique ID.
def get_user(cur, user_id):
    cur.execute("SELECT user_id, user_name FROM Users WHERE user_ID = ?", (user_id,))
    return cur.fetchone()


# All the habits and their data will be gathered from the selected user.
def get_habits_for_user(cur, user_id):
    cur.execute("""
        SELECT habit_ID, habit_name, frequency, start_date, start_time, check_date, check_time,
               longest_streak, current_streak, failed_attempt_count
        FROM Habits
        WHERE user_id = ?
        ORDER BY habit_ID;
    """, (user_id,))
    return cur.fetchall()


# All information from a habit will be gathered using the habit's ID.
def get_habit(cur, habit_id):
    cur.execute("""
        SELECT habit_id, user_id, habit_name, frequency, start_date, check_date,
               longest_streak, current_streak, failed_attempt_count
        FROM Habits
        WHERE habit_id = ?;
    """, (habit_id,))
    return cur.fetchone()


# The habits name will be return using the habits ID.
def get_habit_name(cur, habit_id):
    cur.execute("""
        SELECT habit_name FROM Habits WHERE habit_id = ?;
    """, (habit_id,))
    row = cur.fetchone()
    return row[0] if row else None


# Delete a habit by its habit_ID.
def delete_habits(cur, habit_id):
    cur.execute("DELETE FROM Habits WHERE habit_id = ?", (habit_id,))
    return cur.rowcount


# Delete a user by a user ID.
def delete_user(cur, user_id):
    cur.execute("DELETE FROM Users WHERE user_id = ?", (user_id,))
    return cur.rowcount


# returns a habits check date. This is done by using the habit_ID
def get_habit_check_date(cur, habit_id):
    cur.execute("""
        SELECT check_date FROM Habits WHERE habit_id = ?;
    """, (habit_id,))
    row = cur.fetchone()
    return row[0] if row else None


# returns a habits start date. This is done by using the habit_ID
def get_habit_start_date(cur, habit_id):
    cur.execute("""
        SELECT start_date FROM Habits WHERE habit_id = ?;
    """, (habit_id,))
    row = cur.fetchone()
    return row[0] if row else None


# Returns information from habits with the same frequency.
def get_habits_with_the_same_frequency(cur, user_id, frequency):
    cur.execute("""
        SELECT habit_id, habit_name, frequency, start_date, start_time, check_date, check_time,
               longest_streak, current_streak, failed_attempt_count
        FROM Habits
        WHERE user_id = ? AND frequency = ?
    """, (user_id, frequency))
    return cur.fetchall()


# Returns the habit with the longest streak. only returns the habit ID, name and longest streak count.
def get_longest_streak_of_all_habits(cur, user_id):
    cur.execute("""
        SELECT habit_ID, habit_name, longest_streak
        FROM Habits
        WHERE user_id = ?
        ORDER BY longest_streak DESC
        LIMIT 1;
    """, (user_id,))
    return cur.fetchall()


# Returns the longest streak from a given habit.
def get_longest_streak_from_habit_x(cur, habit_id):
    cur.execute("""
       SELECT longest_streak
        FROM Habits
        WHERE habit_id = ? 
    """, (habit_id,))
    row = cur.fetchone()
    return row[0] if row else None


# insert full habit data
def insert_full_habit(cur, user_id, habit: Habit, longest_streak, current_streak, failed_attempt_count, habit_id=None):
    cols = ["user_id", "habit_name", "frequency", "start_date", "start_time", "check_date", "check_time",
            "longest_streak", "current_streak", "failed_attempt_count"]
    vals = [user_id, habit.habit_name, habit.frequency, habit.created_date, habit.created_time, habit.check_date,
            habit.check_time, longest_streak, current_streak, failed_attempt_count]

    if habit_id is None:
        cur.execute(f"""
                INSERT INTO Habits ({", ".join(cols)})
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(vals))
        return cur.lastrowid
    else:
        cols = ["habit_id"] + cols
        vals = [habit_id] + vals
        placeholders = ", ".join(["?"] * len(vals))
        cur.execute(f"""
                INSERT INTO Habits ({", ".join(cols)})
                VALUES ({placeholders})
            """, tuple(vals))
        return habit_id
