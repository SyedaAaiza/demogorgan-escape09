import json
import os

# JSON file UI folder ke andar hi save ho gi
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HIGH_SCORE_FILE = os.path.join(BASE_DIR, "highscore.json")

def load_high_score():
    """JSON file se highest score load karta hai."""
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                data = json.load(f)
                return data.get("high_score", 0)
        except Exception as e:
            print("High score load nahi ho saka:", e)
    return 0

def save_high_score(new_score):
    """Naya high score hone par JSON mein update karta hai."""
    current_high = load_high_score()
    if new_score > current_high:
        try:
            with open(HIGH_SCORE_FILE, "w") as f:
                json.dump({"high_score": int(new_score)}, f, indent=4)
            print(f"Naya High Score Save ho gaya: {new_score}")
            return int(new_score)
        except Exception as e:
            print("High score save nahi ho saka:", e)
    return current_high