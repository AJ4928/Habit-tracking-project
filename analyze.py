from db import (get_db, get_habits_for_user, get_habits_with_the_same_frequency, get_longest_streak_of_all_habits,
                get_longest_streak_from_habit_x)


# returns a list of all habits from a user.
def return_habit_list(user_id):
    db = get_db("user_database_information.db")
    cur = db.cursor()
    habits = get_habits_for_user(cur, user_id)
    return habits


# returns a list of habits with the same frequency
def return_habits_with_same_frequency(user_id, frequency):
    db = get_db("user_database_information.db")
    cur = db.cursor()
    habits = get_habits_with_the_same_frequency(cur, user_id, frequency)
    return habits


# returns a habit that has the longest streak.
def return_habit_with_longest_streak_from_all_habits(user_id):
    db = get_db("user_database_information.db")
    cur = db.cursor()
    habit = get_longest_streak_of_all_habits(cur, user_id)
    return habit


# returns the streak from a given habit
def return_longest_streak_from_named_habit(habit_id):
    db = get_db("user_database_information.db")
    cur = db.cursor()
    habit = get_longest_streak_from_habit_x(cur, habit_id)
    return habit
