import boto3
import json
import time
import uuid
import random
from datetime import datetime

# Initialize the Kinesis client
# Ensure your AWS credentials are configured (e.g., via AWS CLI or environment variables)
kinesis_client = boto3.client('kinesis')

# --- Configuration ---
# IMPORTANT: Replace with the actual name of your Kinesis stream after deployment.
# This stream name will be created by the SAM template.
KINESIS_STREAM_NAME = "network-data-stream" 
RECORD_COUNT = 10 # Number of records to generate
DELAY_SECONDS = 1 # Delay between sending each record

def generate_network_data():
    """
    Generates a single simulated network link data record.
    This function mimics the kind of real-time data and hardware might produce.
    """
    link_id = str(uuid.uuid4()) # Unique ID for each network link measurement
    speed_mbps = round(random.uniform(100, 1000), 2) # Simulated network speed
    latency_ms = round(random.uniform(5, 150), 2) # Simulated latency
    packet_loss_rate = round(random.uniform(0, 0.05), 4) # Simulated packet loss
    timestamp = datetime.now().isoformat() # ISO formatted timestamp

    data = {
        "linkId": link_id,
        "speedMbps": speed_mbps,
        "latencyMs": latency_ms,
        "packetLossRate": packet_loss_rate,
        "timestamp": timestamp,
        "region": "eu-west-2" # Example region, can be dynamic
    }
    return data

def send_to_kinesis(stream_name, data):
    """
    Sends a single data record to the specified Kinesis stream.
    """
    try:
        response = kinesis_client.put_record(
            StreamName=stream_name,
            Data=json.dumps(data), # Kinesis expects data as bytes, so convert JSON to string
            PartitionKey=data["linkId"] # Use linkId as partition key for even distribution
        )
        print(f"Successfully sent record for linkId: {data['linkId']} to Kinesis. SequenceNumber: {response['SequenceNumber']}")
    except Exception as e:
        print(f"Error sending record to Kinesis: {e}")

if __name__ == "__main__":
    print(f"Starting data generation for Kinesis stream: {KINESIS_STREAM_NAME}")
    print(f"Generating {RECORD_COUNT} records with a {DELAY_SECONDS} second delay...")

    for i in range(RECORD_COUNT):
        network_data = generate_network_data()
        send_to_kinesis(KINESIS_STREAM_NAME, network_data)
        time.sleep(DELAY_SECONDS) # Pause between sending records

    print("Data generation complete.")
