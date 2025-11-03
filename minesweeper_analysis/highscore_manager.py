import json
import os

# Define the file to store scores and the max number of scores per level
HIGHSCORE_FILE = 'highscores.json'
MAX_SCORES = 10

def load_scores():
    """
    Loads highscores from the JSON file.
    
    Returns:
        dict: A dictionary containing the highscores.
              e.g., {"9x9x10": [("Player1", 15), ("Player2", 20)]}
    """
    if not os.path.exists(HIGHSCORE_FILE):
        return {}  # Return an empty dictionary if the file doesn't exist
    
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            scores = json.load(f)
            return scores
    except json.JSONDecodeError:
        # If the file is corrupted or empty, return empty
        return {}

def save_scores(scores):
    """
    Saves the highscores dictionary to the JSON file.

    Args:
        scores (dict): The dictionary of scores to save.
    """
    try:
        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump(scores, f, indent=4)
    except IOError as e:
        print(f"Error saving highscores: {e}")

def get_scores(config_key):
    """
    Gets the list of highscores for a specific board configuration.

    Args:
        config_key (str): A unique key for the board config, e.g., "9x9x10".

    Returns:
        list: A list of (name, time) tuples, sorted by time.
    """
    scores = load_scores()
    return scores.get(config_key, [])

def add_score(config_key, name, time):
    """
    Adds a new score for a specific configuration.
    It maintains a sorted list of the top MAX_SCORES.

    Args:
        config_key (str): The configuration key (e.g., "9x9x10").
        name (str): The player's name.
        time (int): The player's time in seconds.
    """
    scores = load_scores()
    score_list = scores.get(config_key, [])
    
    # Add the new score
    score_list.append((name, time))
    
    # Sort the list by time (the second element of the tuple)
    score_list.sort(key=lambda x: x[1])
    
    # Keep only the top MAX_SCORES
    scores[config_key] = score_list[:MAX_SCORES]
    
    # Save the updated scores back to the file
    save_scores(scores)

def is_highscore(config_key, time):
    """
    Checks if a given time qualifies as a highscore for the config.

    Args:
        config_key (str): The configuration key.
        time (int): The time to check.

    Returns:
        bool: True if the time is a highscore, False otherwise.
    """
    score_list = get_scores(config_key)
    
    # If the list isn't full, it's automatically a highscore
    if len(score_list) < MAX_SCORES:
        return True
    
    # If the list is full, check if the time is better than the worst score
    # score_list[-1] is the last (and worst) score
    return time < score_list[-1][1]

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    print("Testing Highscore Manager...")
    
    # Test adding some scores
    add_score("test_config", "Alice", 100)
    add_score("test_config", "Bob", 50)
    add_score("test_config", "Charlie", 75)
    
    print("Current scores for 'test_config':")
    scores = get_scores("test_config")
    print(scores)
    
    # Test sorting and max
    for i in range(12):
        add_score("max_test", f"Player{i}", 10 * i)
        
    print("\nCurrent scores for 'max_test' (should only be 10):")
    max_scores = get_scores("max_test")
    print(max_scores)
    print(f"Length: {len(max_scores)}")
    
    # Clean up the test file
    if os.path.exists(HIGHSCORE_FILE):
        os.remove(HIGHSCORE_FILE)
    print("\nCleaned up highscores.json")