import click
import session_store
import os

from analyze import (return_habit_list, return_habits_with_same_frequency,
                     return_habit_with_longest_streak_from_all_habits, return_longest_streak_from_named_habit)

from datetime import datetime

from OOP import (Habit, DateHelper, TimeHelper)

from db import (get_db, create_table_for_users, create_table_for_habits, insert_habit, mark_habit_success,
                mark_habit_fail, get_user, get_habit_name, delete_habits, get_habit_check_date, get_habit_start_date, insert_user, insert_full_habit)


SESSION_FILE = "session.json"


@click.group()
def cli():
    pass


@click.command()
def welcome():
    print("""
    Hello and welcome to my python project.
    
    It is important to note that there is no way to add more users to the database. Thus a predefined database was created with one user on it. This users name is Jhon with the user ID 1.
    To continue pleas login in by using the following command. python main.py login --user_id 1.
    
    OPTIONS:
    welcome [python main.py welcome] shows the welcome screen.
    login   [python main.py login --user_id] this will login in the user who wants to view or change there habit data.
    whoami  [python main.py whoami] this will display the current user name and id.
    create  [python main.py create --habit_name --frequency] example [python main.py create --habit_name Gym --frequency daily]. you can only choose the following frequency options (daily, weekly). Use this command to add new habits.
    analyze [python main.py analyze --habitid --periodicity] example [python main.py analyze --habitid 1 --periodicity daily]. You can only choose the following periodicity options (daily, weekly)
    check   [python main.py check --habitid] be sure to check your habit at the correct time to maintain a streak.
    delete  [python main.py delete --habitid] use this command to delete habits you no longer want to follow

    """)

    db_path = "user_database_information.db"

    def main():
        # If the DB file already exists, stop.
        if os.path.exists(db_path):
            return

        db = get_db(db_path)
        try:
            # create tables
            create_table_for_users(db)
            create_table_for_habits(db)
            db.commit()

            cur = db.cursor()

            insert_user(cur, "Jhon", 1)

            h1info = Habit("Drink 2L of water", "daily", "2025-10-10", "10:00", "2025-10-11", "10:00")
            h2info = Habit("Yoga", "daily", "2025-10-15", "16:00", "2025-10-16", "16:00")
            h3info = Habit("meditate for 10 min", "daily", "2025-11-12", "17:00", "2025-11-11", "17:00")
            h4info = Habit("Go to Gym", "weekly", "2025-10-14", "11:00", "2025-10-21", "11:00")
            h5info = Habit("Water plants", "weekly", "2025-10-21", "10:00", "2025-10-28", "10:00")

            insert_full_habit(cur, 1, h1info, 20, 15, 4)
            insert_full_habit(cur, 1, h2info, 15, 12, 7)
            insert_full_habit(cur, 1, h3info, 10, 4, 12)
            insert_full_habit(cur, 1, h4info, 5, 2, 1)
            insert_full_habit(cur, 1, h5info, 2, 1, 3)

            db.commit()

        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    if __name__ == "__main__":
        main()


@click.command()
@click.option('--user_id', type=int, required=True)
def login(user_id):
    db = get_db("user_database_information.db")
    create_table_for_users(db)
    cur = db.cursor()

    user = get_user(cur, user_id)
    db.close()

    if user is None:
        print("No user found with ID " + str(user_id))
    else:

        session_store.save_current_user_id(user[0])
        print("Logged in as: user ID: " + str(user[0]) + " User name: " + user[1])


@click.command()
def whoami():
    user_id = session_store.load_current_user_id()

    if user_id is None:
        print("No user is currently logged in.")
        return

    db = get_db("user_database_information.db")
    create_table_for_users(db)
    cur = db.cursor()

    user = get_user(cur, user_id)
    if user is None:
        print("User " + user_id + " does not exist in the database.")
        db.close()
        return

    db.close()

    if user is None:
        print("Session says user " + str(user_id) + " no longer exists in the DB.")
    else:

        print("Current user: user ID: " + str(user[0]) + " User name: " + user[1])


@click.command()
@click.option('--habit_name', type=str, required=True)
@click.option('--frequency', type=str, required=True)
def create(habit_name, frequency):
    user_id = session_store.load_current_user_id()

    if user_id is None:
        print("No user is currently logged in.")
        return

    db = get_db("user_database_information.db")
    create_table_for_habits(db)
    cur = db.cursor()

    user = get_user(cur, user_id)
    if user is None:
        print("User " + user_id + " does not exist in the database.")
        db.close()
        return

    time = TimeHelper.now()

    if frequency == "daily":
        check_date = DateHelper.daily()
    elif frequency == 'weekly':
        check_date = DateHelper.weekly()
    else:
        print("check date could not be determined")
        return

    habit_info = Habit(habit_name, frequency, DateHelper.today(), time, check_date, time)

    insert_habit(cur, user[0], habit_info, )

    db.commit()
    print("habit was successfully created")
    db.close()


@click.command()
@click.option('--habitid', type=int, required=True)
@click.option('--periodicity', type=str, required=True)
def analyze(habitid, periodicity):
    user_id = session_store.load_current_user_id()

    if user_id is None:
        print("No user is currently logged in.")
        return

    db = get_db("user_database_information.db")
    create_table_for_users(db)
    cur = db.cursor()

    user = get_user(cur, user_id)
    if user is None:
        print("User " + user_id + " does not exist in the database.")
        db.close()
        return

    habit_name = get_habit_name(cur, habitid)

    print("A list of all habits: ", return_habit_list(user[0]))

    print("\nlist of habits with same frequency: ", return_habits_with_same_frequency(user[0], periodicity))

    print("\nHabit with the longest streak overall [ID, name, days] ",
          return_habit_with_longest_streak_from_all_habits(user[0]))

    print("\nHabit " + habit_name + " longest streak is ", return_longest_streak_from_named_habit(habitid), " days")

    db.close()


@click.command()
@click.option('--habitid', type=int, required=True)
# ch= mark habit compleat
def check(habitid):
    db = get_db("user_database_information.db")
    create_table_for_habits(db)
    cur = db.cursor()

    today_str = DateHelper.today()
    check_date_str = get_habit_check_date(cur, habitid)

    if check_date_str is None:
        print("No check_date set for habit ID " + str(habitid) + " habit doesn't exist")
        db.close()
        return

    today = datetime.strptime(today_str, "%Y-%m-%d").date()
    check_date = datetime.strptime(check_date_str, "%Y-%m-%d").date()

    if today < check_date:
        print("you are too soon. The next check date for habit: " + str(habitid) + " is " + check_date_str)
        db.close()
        return

    elif today == check_date:
        mark_habit_success(cur, habitid)
        db.commit()
        check_date_str = get_habit_check_date(cur, habitid)
        print("you checked your habit for the day. The next check day is " + check_date_str)
        db.close()
        return

    elif today > check_date:
        mark_habit_fail(cur, habitid)
        db.commit()
        new_start_date = get_habit_start_date(cur, habitid)
        new_check_date = get_habit_check_date(cur, habitid)
        print("Sorry you missed your habit check day. Your streak was lost "
              "Here is your new start date and check date "
              "Start: " + new_start_date + "  Check: " + new_check_date)
        db.close()


@click.command()
@click.option('--habitid', type=int, required=True)
def delete(habitid):
    db = get_db("user_database_information.db")
    create_table_for_habits(db)
    cur = db.cursor()

    habit_name = get_habit_name(cur, habitid)

    if habit_name is None:
        print("No habit found with ID" + str(habitid) + " nothing deleted")
        db.close()
        return

    deleted = delete_habits(cur, habitid)
    db.commit()
    db.close()

    if deleted:
        print("Habit ID:" + str(habitid) + " Habit name: " + habit_name + " has been deleted")
    else:

        print("Could not delete habit with ID " + str(habitid))


cli.add_command(welcome)
cli.add_command(login)
cli.add_command(whoami)
cli.add_command(create)
cli.add_command(analyze)
cli.add_command(check)
cli.add_command(delete)

if __name__ == "__main__":
    cli()
