
import os
import sys
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Setup path and env
BASE_DIR = Path(__file__).parent / "backend-cortex"
sys.path.append(str(BASE_DIR))
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_FAST_MODEL", "gemini-flash-lite-latest")

print(f"--- Gemini Diagnostic ---")
print(f"API Key Present: {'Yes' if API_KEY else 'No'}")
print(f"Model Name: {MODEL_NAME}")

if not API_KEY:
    print("FATAL: No API Key found.")
    sys.exit(1)

genai.configure(api_key=API_KEY)

try:
    print("Attempting generation...")
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content("Hello, system check.")
    print(f"Response: {response.text}")
    print("SUCCESS: Generation worked.")
except Exception as e:
    print(f"FAILURE: {e}")
    # Print available models if generation fails
    try:
        print("Listing available models...")
        for m in genai.list_models():
             print(m.name)
    except:
        pass

print("\n--- Embedding Diagnostic ---")
print(f"Embedding Model: models/gemini-embedding-001")
try:
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content="Test embedding vector.",
        task_type="retrieval_document",
        title="Cortex Memory"
    )
    print("SUCCESS: Embedding generated.")
    print(f"Vector Length: {len(result['embedding'])}")
except Exception as e:
    print(f"FAILURE: {e}")
