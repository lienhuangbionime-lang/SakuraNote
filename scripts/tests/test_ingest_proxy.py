
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

URL = "http://localhost:3000/api/py/ingest"
PAYLOAD = {
    "date": "2026-02-15",
    "content": "Test entry to verify system connectivity and vector generation. Need to insure this works.",
    "habits": ["Testing"],
    "skipAi": False, # Enable AI to test crash logic
    "mode": "append"
}

logging.info(f"Sending POST request to {URL}...")
try:
    response = requests.post(URL, json=PAYLOAD, timeout=10)
    
    logging.info(f"Status Code: {response.status_code}")
    try:
        logging.info(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        logging.info(f"Raw text: {response.text}")

    if response.status_code == 200:
        logging.info("SUCCESS: Data ingested via proxy.")
    else:
        logging.error(f"FAILURE: {response.status_code}")

except Exception as e:
    logging.error(f"Request failed: {e}")
