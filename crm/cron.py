import logging
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure logging to append to a file
logging.basicConfig(filename='E:/Coding Workspace/ALX/alx-backend-graphql_crm/tmp/crm_heartbeat_log.txt', level=logging.INFO,
                    format='%(message)s')

def update_low_stock():
    # Generate timestamp in DD/MM/YYYY-HH:MM:SS format
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')

    # GraphQL endpoint
    graphql_url = "http://localhost:8000/graphql"
    transport = RequestsHTTPTransport(url=graphql_url, verify=True, retries=3)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # GraphQL mutation
    mutation = gql("""
        mutation {
            updateLowStockProducts {
                updatedProducts {
                    name
                    stock
                }
                message
            }
        }
    """)

    try:
        result = client.execute(mutation)
        updated_products = result['updateLowStockProducts']['updatedProducts']
        message = result['updateLowStockProducts']['message']

        if updated_products:
            for product in updated_products:
                product_name = product['name']
                new_stock = product['stock']
                log_message = f"{timestamp} - Product: {product_name}, New Stock: {new_stock}"
                logging.info(log_message)
        else:
            logging.info(f"{timestamp} - {message}")
    except Exception as e:
        logging.error(f"{timestamp} - Error updating low stock: {str(e)}")


def log_crm_heartbeat():
    # Generate timestamp in DD/MM/YYYY-HH:MM:SS format
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    heartbeat_message = f"{timestamp} CRM is alive"

    # Log the heartbeat message
    logging.info(heartbeat_message)

    # Verify GraphQL endpoint responsiveness with hello field
    graphql_url = "http://localhost:8000/graphql"
    transport = RequestsHTTPTransport(url=graphql_url, verify=True, retries=3)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    try:
        query = gql("""
            query {
                hello
            }
        """)
        result = client.execute(query)
        hello_message = result.get('hello', 'No response')
        logging.info(f"GraphQL endpoint responsive: {hello_message}")
    except Exception as e:
        logging.error(f"GraphQL health check failed: {str(e)}")



if __name__ == "__main__":
    log_crm_heartbeat(),
    update_low_stock()