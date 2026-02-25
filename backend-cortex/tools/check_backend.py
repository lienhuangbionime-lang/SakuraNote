import sys
import os

sys.path.append(os.path.abspath("."))

print("Checking imports...")

try:
    print("1. Importing app.models.schemas...")
    from app.models.schemas import LogEntrySchema
    print("   [OK]")
except ImportError as e:
    print(f"   [FAIL] {e}")

try:
    print("2. Importing app.core.vector...")
    from app.core.vector import vector_engine
    print("   [OK]")
except ImportError as e:
    print(f"   [FAIL] {e}")

try:
    print("3. Importing app.api.v1.memories...")
    from app.api.v1 import memories
    print("   [OK]")
except ImportError as e:
    print(f"   [FAIL] {e}")

print("Done.")
