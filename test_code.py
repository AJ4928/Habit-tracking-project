import pytest
import db
import analyze


from datetime import date, timedelta
from OOP import Habit


@pytest.fixture()
def fresh_db(tmp_path, monkeypatch):
    """
    This fixture creates a fresh database for every test.

    Important: analyze.py always uses a file called "user_database_information.db",
    so we change directory into a temp folder so it creates/uses a temp DB.
    """
    monkeypatch.chdir(tmp_path)

    conn = db.get_db("user_database_information.db")
    db.create_table_for_users(conn)
    db.create_table_for_habits(conn)

    cur = conn.cursor()

    # Create a test user with a fixed ID so it is easy to reason about.
    user_id = db.insert_user(cur, "Test User", user_id=1)
    conn.commit()

    yield conn, cur, user_id

    conn.close()


def test_create_habit_inserts_a_row(fresh_db):
    conn, cur, user_id = fresh_db
    habit = Habit("Drink Water", "daily", "2025-01-01", "10:00", "2025-01-02", "10:00")

    habit_id = db.insert_habit(cur, user_id, habit)
    conn.commit()

    row = db.get_habit(cur, habit_id)
    assert row is not None
    assert row[2] == "Drink Water"      # habit_name
    assert row[3] == "daily"            # frequency
    assert row[6] == 0                  # longest_streak default
    assert row[7] == 0                  # current_streak default
    assert row[8] == 0                  # failed_attempt_count default

# TEST_HABITS


def test_create_habit_same_name_for_same_user_should_fail(fresh_db):
    conn, cur, user_id = fresh_db
    habit1 = Habit("Read", "daily", "2025-01-01", "10:00", "2025-01-02", "10:00")
    habit2 = Habit("Read", "weekly", "2025-01-01", "10:00", "2025-01-08", "10:00")

    db.insert_habit(cur, user_id, habit1)
    conn.commit()

    # (this should raise an error because of UNIQUE (user_id, habit_name))
    import sqlite3
    try:
        db.insert_habit(cur, user_id, habit2)
        conn.commit()
        assert False, "Expected UNIQUE constraint error but insert worked"
    except sqlite3.IntegrityError:
        conn.rollback()


def test_edit_habit_mark_success_increases_streak_and_moves_check_date_daily(fresh_db):
    conn, cur, user_id = fresh_db
    habit = Habit("Pushups", "daily", "2025-01-01", "10:00", "2025-01-01", "10:00")
    habit_id = db.insert_habit(cur, user_id, habit)
    conn.commit()

    db.mark_habit_success(cur, habit_id)
    conn.commit()

    updated = db.get_habit(cur, habit_id)
    assert updated[7] == 1   # current_streak
    assert updated[6] == 1   # longest_streak
    assert updated[5] == "2025-01-02"  # check_date moved +1 day from 2025-01-01


def test_edit_habit_mark_success_moves_check_date_weekly(fresh_db):
    conn, cur, user_id = fresh_db
    habit = Habit("Gym", "weekly", "2025-01-01", "10:00", "2025-01-01", "10:00")
    habit_id = db.insert_habit(cur, user_id, habit)
    conn.commit()

    db.mark_habit_success(cur, habit_id)
    conn.commit()

    updated = db.get_habit(cur, habit_id)
    assert updated[5] == "2025-01-08"  # +7 days


def test_edit_habit_mark_fail_resets_current_streak_and_increases_fail_count(fresh_db):
    conn, cur, user_id = fresh_db
    habit = Habit("Meditate", "daily", "2025-01-01", "10:00", "2025-01-01", "10:00")
    habit_id = db.insert_habit(cur, user_id, habit)
    conn.commit()

    # Make a streak first so we can see it reset
    db.mark_habit_success(cur, habit_id)
    conn.commit()

    db.mark_habit_fail(cur, habit_id)
    conn.commit()

    updated = db.get_habit(cur, habit_id)
    assert updated[7] == 0  # current_streak reset
    assert updated[8] == 1  # failed_attempt_count increased

    # mark_habit_fail sets start_date=today and check_date=tomorrow (sqlite date('now'))
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    assert updated[4] == today
    assert updated[5] == tomorrow


def test_delete_habit_removes_it_from_database(fresh_db):
    conn, cur, user_id = fresh_db
    habit = Habit("DeleteMe", "daily", "2025-01-01", "10:00", "2025-01-02", "10:00")
    habit_id = db.insert_habit(cur, user_id, habit)
    conn.commit()

    deleted_count = db.delete_habits(cur, habit_id)
    conn.commit()

    assert deleted_count == 1
    assert db.get_habit_name(cur, habit_id) is None

# TEST_ANALYZE


def test_return_habit_list_returns_all_habits_for_user(fresh_db):
    conn, cur, user_id = fresh_db

    db.insert_habit(cur, user_id, Habit("A", "daily", "2025-01-01", "10:00", "2025-01-02", "10:00"))
    db.insert_habit(cur, user_id, Habit("B", "weekly", "2025-01-01", "10:00", "2025-01-08", "10:00"))
    conn.commit()
    conn.close()  # analyze.py opens its own connection

    habits = analyze.return_habit_list(user_id)

    assert len(habits) == 2
    names = [row[1] for row in habits]
    assert "A" in names
    assert "B" in names


def test_return_habits_with_same_frequency_filters_correctly(fresh_db):
    conn, cur, user_id = fresh_db

    db.insert_habit(cur, user_id, Habit("Daily1", "daily", "2025-01-01", "10:00", "2025-01-02", "10:00"))
    db.insert_habit(cur, user_id, Habit("Daily2", "daily", "2025-01-01", "10:00", "2025-01-02", "10:00"))
    db.insert_habit(cur, user_id, Habit("Weekly1", "weekly", "2025-01-01", "10:00", "2025-01-08", "10:00"))
    conn.commit()
    conn.close()

    daily_habits = analyze.return_habits_with_same_frequency(user_id, "daily")
    weekly_habits = analyze.return_habits_with_same_frequency(user_id, "weekly")

    assert len(daily_habits) == 2
    assert len(weekly_habits) == 1
    assert weekly_habits[0][1] == "Weekly1"


def test_return_habit_with_longest_streak_from_all_habits_returns_the_biggest_one(fresh_db):
    conn, cur, user_id = fresh_db

    # We use insert_full_habit so we can control longest_streak numbers.
    db.insert_full_habit(
        cur, user_id,
        Habit("SmallStreak", "daily", "2025-01-01", "10:00", "2025-01-02", "10:00"),
        longest_streak=3, current_streak=1, failed_attempt_count=0
    )
    db.insert_full_habit(
        cur, user_id,
        Habit("BigStreak", "daily", "2025-01-01", "10:00", "2025-01-02", "10:00"),
        longest_streak=10, current_streak=2, failed_attempt_count=0
    )
    conn.commit()
    conn.close()

    best = analyze.return_habit_with_longest_streak_from_all_habits(user_id)

    # db.get_longest_streak_of_all_habits returns a list (fetchall), so best is also a list
    assert len(best) == 1
    assert best[0][1] == "BigStreak"
    assert best[0][2] == 10


def test_return_longest_streak_from_named_habit_returns_number(fresh_db):
    conn, cur, user_id = fresh_db

    habit_id = db.insert_full_habit(
        cur, user_id,
        Habit("MyHabit", "daily", "2025-01-01", "10:00", "2025-01-02", "10:00"),
        longest_streak=7, current_streak=2, failed_attempt_count=0
    )
    conn.commit()
    conn.close()

    streak = analyze.return_longest_streak_from_named_habit(habit_id)

    assert streak == 7


def test_return_longest_streak_from_named_habit_returns_none_if_not_found(fresh_db):
    conn, cur, user_id = fresh_db
    conn.commit()
    conn.close()

    streak = analyze.return_longest_streak_from_named_habit(999999)

    assert streak is None
