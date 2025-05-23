import json
import boto3
import os
import uuid # Using uuid for more robust unique ID generation
from datetime import datetime

# Initialize the DynamoDB client outside the handler for better performance (warm starts).
# The table name is retrieved from environment variables, which will be set by SAM.
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE_NAME')

# Ensure the table name is set, otherwise raise an error (critical for deployment).
if not table_name:
    raise ValueError("DYNAMODB_TABLE_NAME environment variable is not set.")

table = dynamodb.Table(table_name) # Reference to the DynamoDB table

def lambda_handler(event, context):
    """
    AWS Lambda function to process feedback submissions.
    This function is triggered by an API Gateway POST request.
    It extracts feedback data (name, email, category, rating, comment),
    generates a unique ID, and stores it in DynamoDB.
    """
    
    # Log the incoming event for debugging purposes.
    # This helps in understanding the structure of data sent by API Gateway.
    print(f"Received event: {json.dumps(event)}")

    # Define CORS headers for the API Gateway response.
    # This is crucial for web browsers to allow requests from your S3-hosted frontend
    # to your API Gateway endpoint, preventing "CORS Origin" errors.
    cors_headers = {
        "Access-Control-Allow-Origin": "*",  # Allows access from any origin (e.g., your S3 website)
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token", # Required headers for preflight
        "Access-Control-Allow-Methods": "POST,OPTIONS" # Specify allowed methods for preflight (OPTIONS) and actual request (POST)
    }

    # Handle OPTIONS requests (CORS preflight).
    # Browsers send an OPTIONS request before the actual POST request to check CORS permissions.
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': '' # Empty body for OPTIONS response
        }

    # Process POST requests for feedback submission.
    elif event['httpMethod'] == 'POST':
        try:
            # Parse the JSON body from the API Gateway event.
            # The frontend now sends the direct JSON payload, so only one json.loads is needed.
            body = json.loads(event['body'])

            # Extract feedback details from the parsed body.
            # Using .get() with a default value prevents KeyError if a field is optional/missing.
            name = body.get('name', 'Anonymous')
            email = body.get('email', 'N/A')
            category = body.get('category', 'General')
            rating = body.get('rating', 0) # Default rating to 0 if not provided
            comment = body.get('comment', '').strip() # Get comment and remove leading/trailing whitespace
            
            # Validate required fields 
            if not name:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'success': False, 'error': 'Feedback name cannot be empty.'})
                }
            if not email:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'success': False, 'error': 'Feedback email cannot be empty.'})
                }
            if not comment:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'success': False, 'error': 'Feedback comment cannot be empty.'})
                }
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'success': False, 'error': 'Rating must be an integer between 1 and 5.'})
                }

            # Generate a unique ID for the feedback entry.
            # uuid.uuid4() generates a universally unique identifier, which is robust.
            feedback_id = str(uuid.uuid4())
            
            # Get the current timestamp in ISO format.
            # This helps in tracking when the feedback was received.
            timestamp = datetime.now().isoformat()

            # Prepare the item to be stored in DynamoDB.
            # 'feedback_id' is the partition key for the DynamoDB table.
            # Ensure keys match the DynamoDB table schema (case-sensitive).
            item = {
                'feedback_id': feedback_id, # Primary Key
                'Name': name,
                'Email': email,
                'Category': category,
                'Rating': rating,
                'Comment': comment,
                'Timestamp': timestamp # Store the timestamp
            }

            # Put the item into the DynamoDB table.
            # This is the core operation that saves the feedback data.
            table.put_item(Item=item)

            # Log success message and the ID of the stored feedback.
            print(f"Feedback {feedback_id} stored successfully.")

            # Return a success response to API Gateway.
            # The 'body' contains a JSON message indicating success.
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'success': True,
                    'message': 'Feedback submitted successfully!',
                    'feedbackId': feedback_id
                })
            }

        except json.JSONDecodeError as e:
            # Handle cases where the request body is not valid JSON.
            print(f"JSON Decode Error: {e}")
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'success': False, 'error': 'Invalid JSON in request body.'})
            }
        except KeyError as e:
            # Handle cases where expected fields are missing from the request body.
            # Although .get() is used, this catch is a safeguard for unexpected structures.
            print(f"Missing Key Error: {e}")
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'success': False, 'error': f'Missing expected field: {e}'})
            }
        except Exception as e:
            # Catch any other unexpected errors during processing.
            print(f"An unexpected error occurred: {e}")
            return {
                'statusCode': 500,
                'headers': cors_headers,
                'body': json.dumps({'success': False, 'error': f'Internal server error: {str(e)}'})
            }
    
    # Handle any other HTTP methods not explicitly supported (e.g., GET, PUT, DELETE).
    else:
        return {
            'statusCode': 405, # Method Not Allowed
            'headers': cors_headers,
            'body': json.dumps({'success': False, 'error': 'Method Not Allowed'})
        }

