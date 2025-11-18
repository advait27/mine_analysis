import os
import sys

print("\n--- STARTING DIAGNOSTIC ---")

# 1. Check if the manager python file exists
if not os.path.exists("highscore_manager.py"):
    print("❌ ERROR: 'highscore_manager.py' not found.")
    print("   Make sure you saved it in the same folder as this script.")
    sys.exit(1)
print("✅ check: highscore_manager.py found.")

# 2. Clean up old json file (Force Reset)
if os.path.exists("highscores.json"):
    try:
        os.remove("highscores.json")
        print("✅ check: Deleted old 'highscores.json' to ensure a fresh start.")
    except Exception as e:
        print(f"⚠️ WARNING: Could not delete 'highscores.json': {e}")
        print("   Please manually delete this file and run again.")

# 3. Try to import the module
try:
    # Ensure the script directory is on sys.path so local modules can be found
    script_dir = os.path.abspath(os.path.dirname(__file__)) if '__file__' in globals() else os.getcwd()
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    # Try a normal import first, then fall back to importing by file path to satisfy linters
    try:
        import highscore_manager as hs
        print(f"✅ check: Imported module from: {hs.__file__}")
    except ImportError:
        # Fallback: load the module directly from highscore_manager.py in the script directory
        import importlib.util
        module_path = os.path.join(script_dir, "highscore_manager.py")
        if os.path.exists(module_path):
            spec = importlib.util.spec_from_file_location("highscore_manager", module_path)
            hs = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(hs)
            print(f"✅ check: Imported module from file: {module_path}")
        else:
            # Re-raise ImportError to be handled by the outer exception handlers
            raise
except ImportError as e:
    print(f"❌ ERROR: Could not import module: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERROR: Crashed during import: {e}")
    sys.exit(1)

# 4. Check if the specific function exists
if hasattr(hs, 'get_scores'):
    print("✅ check: Function 'get_scores' exists.")
else:
    print("❌ ERROR: Function 'get_scores' is MISSING inside highscore_manager.py.")
    print("   Please Open highscore_manager.py and ensure you pasted the code correctly.")
    sys.exit(1)

# 5. Test the function logic
try:
    result = hs.get_scores("test_key_999")
    print(f"✅ check: hs.get_scores returned: {result}")
    
    if isinstance(result, list):
        print("✅ check: Return type is correct (list).")
    else:
        print(f"❌ ERROR: Return type is wrong. Expected list, got {type(result)}.")
        print("   This usually means load_scores() is failing to return a dictionary internally.")
except AttributeError as e:
    print("\n❌ ERROR: ATTRIBUTE ERROR CAUGHT!")
    print(f"   Error detail: {e}")
    print("   EXPLANATION: This usually happens if 'highscores.json' contains a List []")
    print("   instead of a Dictionary {}. The 'bulletproof' code I provided fixes this.")
    print("   If you see this, you are likely NOT running the latest version of highscore_manager.py.")
except Exception as e:
    print(f"❌ ERROR: Crashed while running function: {e}")

print("\n--- DIAGNOSTIC COMPLETE ---")