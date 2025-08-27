import requests
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
import logging

# Configure logging to append to a file
logging.basicConfig(filename='/tmp/crm_report_log.txt', level=logging.INFO,
                    format='%(message)s')

@shared_task
def generate_crm_report():
    # GraphQL endpoint
    graphql_url = "http://localhost:8000/graphql"
    transport = RequestsHTTPTransport(url=graphql_url, verify=True, retries=3)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # GraphQL query to fetch CRM report data
    query = gql("""
        query {
            totalCustomers
            totalOrders
            totalRevenue
        }
    """)

    try:
        result = client.execute(query)
        total_customers = result.get('totalCustomers', 0)
        total_orders = result.get('totalOrders', 0)
        total_revenue = result.get('totalRevenue', 0.0)

        # Generate timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue"
        logging.info(report_message)
    except Exception as e:
        logging.error(f"{timestamp} - Error generating CRM report: {str(e)}")