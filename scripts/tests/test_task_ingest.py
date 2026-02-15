
import requests
import json
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

URL = "http://localhost:3000/api/py/ingest"

# Test Content with clear tasks
PAYLOAD = {
    "date": "2026-02-15",
    "content": "Project Beta Update:\n- [ ] Review system architecture #LifeOS\n- [ ] Deploy hotfix for API #LifeOS",
    "skipAi": False 
}

logging.info(f"Sending Task Ingest Test to {URL}...")
try:
    response = requests.post(URL, json=PAYLOAD, timeout=60) # Longer timeout for AI
    
    logging.info(f"Status Code: {response.status_code}")
    logging.info(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        ai_data = data.get("data", {})
        tasks = ai_data.get("tasks", [])
        logging.info(f"AI Detected {len(tasks)} tasks.")
        if len(tasks) > 0:
            logging.info("SUCCESS: AI detected tasks.")
            logging.info("Check backend logs to confirm DB insertion 'Successfully created X tasks'.")
        else:
            logging.warning("AI did not detect tasks. Prompt might need adjustment or inputs were too vague.")
            
except Exception as e:
    logging.error(f"Test failed: {e}")
