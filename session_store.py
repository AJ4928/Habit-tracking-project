import json
import os

SESSION_FILE = "session.json"

def save_current_user_id(user_id: int):
    with open(SESSION_FILE, "w") as f:
        json.dump({"user_id": user_id}, f)

def load_current_user_id():
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
        return data.get("user_id")
    except Exception:
        return None