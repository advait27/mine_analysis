import json
import os

HIGHSCORE_FILE = 'highscores.json'
MAX_SCORES = 10

def load_scores():
    """
    Loads highscores from the JSON file.
    Safeguards against file corruption or incorrect data types.
    """
    if not os.path.exists(HIGHSCORE_FILE):
        return {}
    
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            data = json.load(f)
            # CRITICAL CHECK: Ensure data is actually a dictionary
            if not isinstance(data, dict):
                print("Warning: Highscore file format incorrect. Resetting.")
                return {}
            return data
    except (json.JSONDecodeError, IOError):
        print("Warning: Highscore file corrupted. Starting fresh.")
        return {}

def save_scores(scores):
    """Saves the highscores dictionary to the JSON file."""
    try:
        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump(scores, f, indent=4)
    except IOError as e:
        print(f"Error saving highscores: {e}")

def get_scores(config_key):
    """
    Gets the list of highscores for a specific board configuration.
    """
    scores = load_scores()
    # Ensure we return a list, even if the key is missing
    return scores.get(config_key, [])

def add_score(config_key, name, time):
    """
    Adds a new score, sorts it, and saves the top 10.
    """
    scores = load_scores()
    
    # Get existing list or create new one
    score_list = scores.get(config_key, [])
    if not isinstance(score_list, list):
        score_list = []

    # Add new score
    score_list.append((name, time))
    
    # Sort by time (ascending)
    score_list.sort(key=lambda x: x[1])
    
    # Keep only top 10
    scores[config_key] = score_list[:MAX_SCORES]
    
    save_scores(scores)

def is_highscore(config_key, time):
    """
    Checks if a given time qualifies as a highscore.
    """
    score_list = get_scores(config_key)
    
    if len(score_list) < MAX_SCORES:
        return True
    
    # Compare with the worst (last) score in the list
    return time < score_list[-1][1]

# --- TEST BLOCK ---
# You can run this file directly to verify it works
if __name__ == "__main__":
    print("Testing Highscore Manager...")
    # Force a save to ensure file creation works
    add_score("test_9x9x10", "TestPlayer", 999)
    print("Scores:", get_scores("test_9x9x10"))
    print("Manager seems to be working.")