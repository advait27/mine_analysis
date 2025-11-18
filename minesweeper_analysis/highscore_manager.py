import json
import os

HIGHSCORE_FILE = 'highscores.json'
MAX_SCORES = 10

def load_scores():
    """
    Loads highscores from the JSON file with strict error checking.
    If the file is corrupted or in the wrong format (like a list),
    it automatically resets to an empty dictionary to prevent crashes.
    """
    if not os.path.exists(HIGHSCORE_FILE):
        return {}
    
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            data = json.load(f)
            
            # --- CRITICAL FIX FOR ATTRIBUTE ERROR ---
            # If the file contains a list [] instead of a dict {}, 
            # standard code crashes. This detects and fixes it.
            if not isinstance(data, dict):
                print(f"Warning: {HIGHSCORE_FILE} was the wrong format. Resetting it.")
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
    Safe to call even if the key doesn't exist yet.
    """
    scores = load_scores()
    # This .get() is what was crashing before if scores was a list.
    # load_scores() above guarantees 'scores' is now a dict.
    return scores.get(config_key, [])

def add_score(config_key, name, time):
    """
    Adds a new score, sorts it, and saves the top 10.
    """
    scores = load_scores()
    
    # Get existing list or create new one if missing
    score_list = scores.get(config_key, [])
    
    # Double check that score_list is actually a list
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
    
    # If we have fewer than 10 scores, it's automatically a highscore
    if len(score_list) < MAX_SCORES:
        return True
    
    # Otherwise, check if it's faster than the slowest (last) score
    return time < score_list[-1][1]