import boto3
import random
import time
from datetime import datetime

# Initialize the CloudWatch client
# This script assumes AWS credentials are configured on the EC2 instance
# via an IAM role (instance profile) with sufficient permissions.
cloudwatch = boto3.client('cloudwatch')

# --- Configuration ---
# Namespace for your custom CloudWatch metric.
# It's good practice to use a unique namespace for your application.
CLOUDWATCH_NAMESPACE = "NetworkApp"
# Name of the custom metric that will represent "users logged in".
METRIC_NAME = "UsersLoggedIn"
# How often to publish the metric (in seconds).
PUBLISH_INTERVAL_SECONDS = 10
# Simulation parameters for user count.
MIN_USERS = 5
MAX_USERS = 50
# How much the user count can change in each interval.
USER_CHANGE_STEP = 5

def publish_custom_metric(metric_value):
    """
    Publishes a custom metric to AWS CloudWatch.
    """
    try:
        cloudwatch.put_metric_data(
            Namespace=CLOUDWATCH_NAMESPACE,
            MetricData=[
                {
                    'MetricName': METRIC_NAME,
                    'Value': metric_value,
                    'Unit': 'Count', # Unit of the metric (e.g., Count, Percent, Bytes)
                    'Timestamp': datetime.utcnow() # Use UTC timestamp
                },
            ]
        )
        print(f"Published metric '{METRIC_NAME}' with value: {metric_value} to CloudWatch.")
    except Exception as e:
        print(f"Error publishing metric to CloudWatch: {e}")

def simulate_user_activity():
    """
    Simulates a fluctuating number of logged-in users.
    """
    current_users = random.randint(MIN_USERS, MAX_USERS)
    while True:
        # Simulate changes in user count
        change = random.randint(-USER_CHANGE_STEP, USER_CHANGE_STEP)
        current_users = max(MIN_USERS, min(MAX_USERS, current_users + change))
        
        # Publish the simulated user count to CloudWatch
        publish_custom_metric(current_users)
        
        # Wait for the next publishing interval
        time.sleep(PUBLISH_INTERVAL_SECONDS)

if __name__ == "__main__":
    print(f"Starting {METRIC_NAME} simulator and CloudWatch publisher...")
    print(f"Metrics will be published to Namespace: {CLOUDWATCH_NAMESPACE}")
    simulate_user_activity()
