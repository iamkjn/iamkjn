import boto3
import json
import time
import random
from datetime import datetime

# Initialize the SQS client
# Ensure your AWS credentials are configured (e.g., via AWS CLI or environment variables)
sqs_client = boto3.client('sqs')

# --- Configuration ---
# IMPORTANT: Replace with the actual URL of your SQS queue after deployment.
# This URL will be an output from your SAM deployment.
SQS_QUEUE_URL = "YOUR_SQS_QUEUE_URL_HERE" 
MESSAGE_COUNT = 5 # Number of messages to send
DELAY_SECONDS = 2 # Delay between sending each message

def generate_customer_request_data():
    """
    Generates a simulated customer web application request.
    This mimics a user interaction or configuration update.
    """
    request_id = f"req-{int(time.time() * 1000)}-{random.randint(1000, 9999)}"
    user_id = f"user-{random.randint(1, 100)}"
    action = random.choice(["update_device_config", "check_network_status", "submit_feedback"])
    device_id = f"dev-{random.randint(10000, 99999)}" if action == "update_device_config" else None
    priority = random.choice(["high", "medium", "low"])
    timestamp = datetime.now().isoformat()

    data = {
        "requestId": request_id,
        "userId": user_id,
        "action": action,
        "deviceId": device_id,
        "priority": priority,
        "timestamp": timestamp,
        "source": "CustomerWebApp"
    }
    return data

def send_message_to_sqs(queue_url, message_body):
    """
    Sends a single message to the specified SQS queue.
    """
    try:
        response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message_body) # SQS MessageBody must be a string
        )
        print(f"Successfully sent message to SQS. MessageId: {response['MessageId']}")
    except Exception as e:
        print(f"Error sending message to SQS: {e}")

if __name__ == "__main__":
    if SQS_QUEUE_URL == "YOUR_SQS_QUEUE_URL_HERE":
        print("ERROR: Please update SQS_QUEUE_URL in this script with your actual SQS queue URL after deployment.")
        exit(1)

    print(f"Starting simulated Customer Web App sending messages to SQS: {SQS_QUEUE_URL}")
    print(f"Sending {MESSAGE_COUNT} messages with a {DELAY_SECONDS} second delay...")

    for i in range(MESSAGE_COUNT):
        request_data = generate_customer_request_data()
        send_message_to_sqs(SQS_QUEUE_URL, request_data)
        time.sleep(DELAY_SECONDS) # Pause between sending messages

    print("Simulated Customer Web App message sending complete.")
