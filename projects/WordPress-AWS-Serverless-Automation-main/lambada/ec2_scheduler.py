import boto3
import json
import logging

# Configure logging for the Lambda function
logger = logging.getLogger()
logger.setLevel(logging.INFO) # Set logging level to INFO for general messages

def handler(event, context):
    """
    Lambda handler function to start or stop EC2 instances based on the
    'action' and 'instance_id' provided in the event input from CloudWatch Events.

    Expected event input structure:
    {
      "action": "start"|"stop",
      "instance_id": "i-xxxxxxxxxxxxxxxxx"
    }
    """
    ec2 = boto3.client('ec2') # Initialize the EC2 client using boto3

    # Extract instance_id and action from the event payload
    instance_id = event.get('instance_id')
    action = event.get('action')

    # Basic input validation
    if not instance_id:
        logger.error("Error: Instance ID not provided in the event input.")
        return {
            'statusCode': 400,
            'body': json.dumps('Error: Instance ID is required.')
        }

    if action not in ['start', 'stop']:
        logger.error(f"Error: Invalid action '{action}' specified for instance {instance_id}. Must be 'start' or 'stop'.")
        return {
            'statusCode': 400,
            'body': json.dumps(f"Error: Invalid action '{action}'.")
        }

    try:
        if action == 'start':
            # Attempt to start the EC2 instance
            logger.info(f"Attempting to start instance: {instance_id}")
            response = ec2.start_instances(InstanceIds=[instance_id], DryRun=False)
            logger.info(f"Start instance response: {json.dumps(response)}")
            message = f"Successfully initiated start for instance {instance_id}."
        elif action == 'stop':
            # Attempt to stop the EC2 instance
            logger.info(f"Attempting to stop instance: {instance_id}")
            response = ec2.stop_instances(InstanceIds=[instance_id], DryRun=False)
            logger.info(f"Stop instance response: {json.dumps(response)}")
            message = f"Successfully initiated stop for instance {instance_id}."

        # Return a successful response
        return {
            'statusCode': 200,
            'body': json.dumps(message)
        }

    except ec2.exceptions.ClientError as e:
        # Handle specific EC2 client errors (e.g., instance already in desired state)
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == 'IncorrectInstanceState':
            logger.warning(f"Instance {instance_id} is already in the target state ({action}). No action taken.")
            return {
                'statusCode': 200,
                'body': json.dumps(f"Instance {instance_id} is already {action}ed.")
            }
        else:
            logger.error(f"AWS EC2 Client Error for {instance_id} during {action}: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps(f"AWS EC2 Client Error: {str(e)}")
            }
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"Unexpected error processing action '{action}' for instance {instance_id}: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Unexpected error: {str(e)}")
        }