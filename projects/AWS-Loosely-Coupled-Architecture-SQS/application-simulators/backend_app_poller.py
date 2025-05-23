import boto3
import json
import time
import os

# Initialize the SQS client
# Ensure your AWS credentials are configured (e.g., via AWS CLI or environment variables)
sqs_client = boto3.client('sqs')

# Initialize the RDS Data API client for Aurora Serverless.
# This client is used to interact with Aurora Serverless databases without needing a direct connection.
rds_client = boto3.client('rds-data')

# --- Configuration ---
# IMPORTANT: Replace with the actual URL of your SQS queue after deployment.
# This URL will be an output from your SAM deployment.
SQS_QUEUE_URL = "YOUR_SQS_QUEUE_URL_HERE"
POLL_INTERVAL_SECONDS = 5 # How often the backend app polls the queue
MAX_MESSAGES = 10 # Maximum number of messages to retrieve per poll (max 10 for SQS)
VISIBILITY_TIMEOUT_SECONDS = 30 # How long messages are invisible after being read

# IMPORTANT: Replace with your actual Aurora Serverless Cluster ARN and Database Name
# These values are required for the RDS Data API to connect to your database.
DB_CLUSTER_ARN = "arn:aws:rds:REGION:ACCOUNT_ID:cluster:YOUR_AURORA_CLUSTER_NAME"
DB_SECRET_ARN = "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:YOUR_DB_SECRET_NAME"
DATABASE_NAME = "your_database_name"
TABLE_NAME = "network_configs" # Example table name in your RDS database

def poll_messages_from_sqs(queue_url, max_messages, visibility_timeout):
    """
    Polls messages from the SQS queue.
    Messages are made invisible for the duration of the VisibilityTimeout.
    """
    try:
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_messages,
            VisibilityTimeout=visibility_timeout,
            WaitTimeSeconds=20 # Long polling: wait up to 20 seconds for messages
        )
        messages = response.get('Messages', [])
        return messages
    except Exception as e:
        print(f"Error polling messages from SQS: {e}")
        return []

def process_message(message_body):
    """
    Simulates processing a message received from SQS.
    In a real scenario, this would involve business logic,
    e.g., updating an RDS database, calling other services.
    """
    try:
        # Parse the message body (which is a JSON string)
        data = json.loads(message_body)
        print(f"Processing Request ID: {data.get('requestId')}, Action: {data.get('action')}")
        
        # Ensure DB_CLUSTER_ARN, DB_SECRET_ARN, DATABASE_NAME, and TABLE_NAME are configured above.
        
        # Assumes a table named 'network_configs' with columns:
        # id (VARCHAR), user_id (VARCHAR), device_id (VARCHAR), action (VARCHAR), timestamp (TIMESTAMP)
        sql_statement = f"INSERT INTO {TABLE_NAME} (id, user_id, device_id, action, timestamp) VALUES (:id, :user_id, :device_id, :action, :timestamp);"
        
        # Parameters for the SQL statement.
        # Ensure data types match your database schema.
        # For numerical data, you might use Decimal(data.get('some_number')) if your DB column is DECIMAL.
        sql_parameters = [
            {'name': 'id', 'value': {'stringValue': data.get('requestId')}},
            {'name': 'user_id', 'value': {'stringValue': data.get('userId')}},
            {'name': 'device_id', 'value': {'stringValue': data.get('deviceId')}},
            {'name': 'action', 'value': {'stringValue': data.get('action')}},
            {'name': 'timestamp', 'value': {'stringValue': data.get('timestamp')}}
        ]

        try:
            response = rds_client.execute_statement(
                resourceArn=DB_CLUSTER_ARN,
                secretArn=DB_SECRET_ARN,
                database=DATABASE_NAME,
                sql=sql_statement,
                parameters=sql_parameters
            )
            print(f"  --> Data for Request ID {data.get('requestId')} successfully inserted into RDS.")
            # print(f"RDS Data API Response: {response}") # Uncomment for detailed response
        except Exception as rds_error:
            print(f"  --> ERROR inserting data into RDS for Request ID {data.get('requestId')}: {rds_error}")
            return False # Indicate failure if DB update fails


        return True # Indicate successful processing
    except json.JSONDecodeError as e:
        print(f"Error decoding message body JSON: {e} - Body: {message_body}")
        return False
    except Exception as e:
        print(f"Error processing message: {e}")
        return False

def delete_message_from_sqs(queue_url, receipt_handle):
    """
    Deletes a message from the SQS queue after it has been successfully processed.
    """
    try:
        sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        print(f"Successfully deleted message with ReceiptHandle: {receipt_handle}")
    except Exception as e:
        print(f"Error deleting message from SQS: {e}")

if __name__ == "__main__":
    if SQS_QUEUE_URL == "YOUR_SQS_QUEUE_URL_HERE":
        print("ERROR: Please update SQS_QUEUE_URL in this script with your actual SQS queue URL after deployment.")
        exit(1)
    
    # Check if RDS configuration is set for the Data API example
    if DB_CLUSTER_ARN == "arn:aws:rds:REGION:ACCOUNT_ID:cluster:YOUR_AURORA_CLUSTER_NAME" or \
       DB_SECRET_ARN == "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:YOUR_DB_SECRET_NAME" or \
       DATABASE_NAME == "your_database_name":
        print("WARNING: RDS Data API configuration (DB_CLUSTER_ARN, DB_SECRET_ARN, DATABASE_NAME) is not updated. "
              "The RDS update part of the script will not function correctly.")
        print("Please update these variables in the script if you intend to test RDS integration.")


    print(f"Starting simulated Backend App polling SQS: {SQS_QUEUE_URL}")

    while True:
        print(f"\nPolling SQS for messages (next poll in {POLL_INTERVAL_SECONDS} seconds)...")
        messages = poll_messages_from_sqs(SQS_QUEUE_URL, MAX_MESSAGES, VISIBILITY_TIMEOUT_SECONDS)

        if messages:
            print(f"Received {len(messages)} message(s).")
            for message in messages:
                message_body = message['Body']
                receipt_handle = message['ReceiptHandle']
                
                if process_message(message_body):
                    delete_message_from_sqs(SQS_QUEUE_URL, receipt_handle)
                else:
                    # If processing fails, the message will become visible again after VisibilityTimeout
                    print(f"Failed to process message. It will reappear in queue after {VISIBILITY_TIMEOUT_SECONDS} seconds.")
        else:
            print("No messages received.")
        
        time.sleep(POLL_INTERVAL_SECONDS) # Wait before the next poll
