import requests
import json

url = "http://localhost:8000/api/v1/ingest"
payload = {
    "text": "Today I feel great! #life",
    "date": "2026-02-12"
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
