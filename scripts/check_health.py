
import sys
import os
import traceback

# Add backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend-cortex"))

print("Attempting to import main app...")

try:
    # Change working directory so relative imports in main.py works
    os.chdir("backend-cortex")
    from main import app
    print("SUCCESS: Application imported successfully.")
except Exception:
    print("CRITICAL ERROR during Startup Import:")
    traceback.print_exc()
