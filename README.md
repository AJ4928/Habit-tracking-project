# Habit Tracker CLI Project

A command-line habit tracker written in Python using SQLite.  
It lets you:

- Create habits with a frequency (daily or weekly)
- Check off habits and track streaks
- Automatically update the next check date
- Failed habit checks reset the streak and create a new start/check date.
- View analytics (all habits, habits by frequency, longest streaks)
- Delete habits


---

## Project Structure

Typical layout:

```text
├── db.py                           # Database helpers (tables, inserts, queries, updates)
├── OOP.py                          # Habit class + DateHelper + TimeHelper
├── analyze.py                      # Helper functions that return analytics data
├── main.py                         # Click-based command line interface  
├── session_store.py                # Stores and loads the current user session
├── test_code.py                    # Pytest test suite
├── requirements.txt                # Shows what is needed to run the project
└── README.md 
```

---

## Requirements and Install

The following is needed to run the program:

```
Python 3.8+
SQLite3 (bundled with Python)
click (CLI framework)           
```
install click with
```
pip install click
```

---

## How to use


1. copy all the files and past in a single project folder.
2. Open the project folder in PyCharm (or any IDE).
3. Open the terminal in the project root (the folder containing main.py).
4. Important! The first time you use the terminal you must type python main.py welcome. This will create a db with predefined data.

To display the welcome screen:
```
python main.py welcome
```

---

## Testing

Use pytest to run the test suite:
1. Open the project folder in PyCharm (or any IDE)
2. open the terminal in the project root (the folder containing main.py).
3. type the following. 

```
pytest test_code.py
```

## Results and tests screenshots

![image alt](https://github.com/AJ4928/Habit-tracking-project/blob/22942153e896cdce12724952c6170fd6897c220b/Welcome%20Screenshot.png)


---
![image alt](https://github.com/AJ4928/Habit-tracking-project/blob/ceae0384e2a412bd89901e329baf99bf23c72961/Log%20in%20Screenshot.png)

---
![image alt]()
---











