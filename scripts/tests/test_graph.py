
import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

URL = "http://localhost:8000/api/v1/brain/graph"

logging.info(f"Sending GET request to {URL}...")
try:
    response = requests.get(URL, timeout=10)
    
    logging.info(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        nodes = data.get("nodes", [])
        links = data.get("links", [])
        logging.info(f"SUCCESS: Graph data received.")
        logging.info(f"Nodes: {len(nodes)}")
        logging.info(f"Links: {len(links)}")
        
        if len(nodes) > 0:
            logging.info(f"Sample Node: {json.dumps(nodes[0], indent=2)}")
    else:
        logging.error(f"FAILURE: {response.text}")

except Exception as e:
    logging.error(f"Request failed: {e}")
