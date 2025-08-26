import logging
from datetime import datetime
import requests

# Configure logging to append to a file
logging.basicConfig(filename='E:/Coding Workspace/ALX/alx-backend-graphql_crm/tmp/crm_heartbeat_log.txt', level=logging.INFO,
                    format='%(message)s')

def log_crm_heartbeat():
    # Generate timestamp in DD/MM/YYYY-HH:MM:SS format
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    heartbeat_message = f"{timestamp} CRM is alive"

    # Log the heartbeat message
    logging.info(heartbeat_message)

    # Optional: Verify GraphQL endpoint responsiveness
    graphql_url = "http://localhost:8000/graphql"
    try:
        response = requests.post(graphql_url, json={'query': '{ hello }'})
        response.raise_for_status()
        graphql_response = response.json()
        if graphql_response.get('data', {}).get('hello'):
            logging.info(f"GraphQL endpoint responsive: {graphql_response['data']['hello']}")
    except requests.exceptions.RequestException as e:
        logging.error(f"GraphQL health check failed: {str(e)}")