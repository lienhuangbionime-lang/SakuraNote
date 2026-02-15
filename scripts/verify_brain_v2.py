
import requests
import json
import sys

# Force UTF-8 for console output to avoid 'charmap' errors
sys.stdout.reconfigure(encoding='utf-8')

URL = "http://localhost:8000/api/py/brain/graph"
# Note: Next.js Rewrites /api/py -> localhost:8000/api/v1
# Let's try direct backend first to rule out Next.js proxy issues
BACKEND_URL = "http://localhost:8000/api/v1/brain/graph"

print(f"Testing Backend Direct: {BACKEND_URL}...")
try:
    response = requests.get(BACKEND_URL, timeout=10) # 10s timeout
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success. Nodes: {len(data.get('nodes', []))}")
    else:
        print(f"Failed. Text: {response.text[:200]}")
except Exception as e:
    print(f"Backend Direct Connection Failed: {e}")

