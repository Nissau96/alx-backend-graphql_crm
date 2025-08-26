import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import timedelta, datetime
import logging

# Configure logging to append to a file
logging.basicConfig(filename='E:/Coding Workspace/ALX/alx-backend-graphql_crm/tmp/order_reminders_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# GraphQL endpoint (adjust if your server runs on a different port or host)
url = "http://localhost:8000/graphql"
transport = RequestsHTTPTransport(url=url, verify=True, retries=3)
client = Client(transport=transport, fetch_schema_from_transport=True)

# Test connection before query
try:
    response = requests.get(url)
    response.raise_for_status()
    logging.info("Successfully connected to GraphQL endpoint")
except requests.exceptions.RequestException as e:
    logging.error(f"Connection test failed: {str(e)}")
    print(f"Connection test failed: {str(e)}")
    exit(1)

# GraphQL query to get pending orders from the last 7 days
query = gql("""
    query {
        orders(order_date_Gte: "%s") {
            id
            order_date
            customer {
                email
            }
        }
    }
""" % (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))

# Execute the query
try:
    result = client.execute(query)
    orders = result.get('orders', [])

    if orders:
        for order in orders:
            order_id = order['id']
            customer_email = order['customer']['email']
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_message = f"Order ID: {order_id}, Customer Email: {customer_email}"
            logging.info(log_message)
    else:
        logging.info("No pending orders found in the last 7 days.")

    print("Order reminders processed!")
except Exception as e:
    logging.error(f"Error processing order reminders: {str(e)}")
    print(f"Error processing order reminders: {str(e)}")