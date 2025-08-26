#!/bin/bash

# Script to clean up inactive customers in the CRM Django app on Windows.
# Deletes customers with no orders in the last year and logs the count.

# Set the absolute path to the project root (adjust this path to your setup)
PROJECT_ROOT="E:/Coding Workspace/ALX/alx-backend-graphql_crm/"

# Change to project root (use / instead of \ for Windows compatibility in Bash)
echo "Changing to directory: $PROJECT_ROOT"
cd "$PROJECT_ROOT" || { echo "Failed to change directory to $PROJECT_ROOT"; exit 1; }
echo "Successfully changed to $PROJECT_ROOT"

# Define log file path and create directory if it doesn't exist
LOG_DIR="E:/Coding Workspace/ALX/alx-backend-graphql_crm/tmp"
LOG_FILE="$LOG_DIR/customer_cleanup_log.txt"
mkdir -p "$LOG_DIR"  # Create tmp directory if it doesn't exist
echo "Log file set to: $LOG_FILE"

# Run Django shell command and capture output, including timestamp in Python
echo "Executing Django shell command..."
DELETED_COUNT=$(python manage.py shell <<'EOF'
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer
from time import strftime

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.exclude(orders__created_at__gte=one_year_ago)
count = inactive_customers.count()
inactive_customers.delete()
timestamp = strftime('%Y-%m-%d %H:%M:%S')
print(f"{timestamp} - Deleted {count} inactive customers.")
EOF
)
echo "Shell command output: $DELETED_COUNT"

# Check if DELETED_COUNT is empty (error occurred) and log it
if [ -z "$DELETED_COUNT" ]; then
    ERROR_TIMESTAMP=$(python -c "from time import strftime; print(strftime('%Y-%m-%d %H:%M:%S'))")
    echo "$ERROR_TIMESTAMP - Error during cleanup. Check Django logs or script output." >> "$LOG_FILE"
    echo "Error logged due to empty DELETED_COUNT"
else
    echo "$DELETED_COUNT" >> "$LOG_FILE"
    echo "Successfully logged deletion count"
fi