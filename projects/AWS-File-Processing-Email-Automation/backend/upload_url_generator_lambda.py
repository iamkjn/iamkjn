import json
import os
import boto3
import uuid

# Initialize S3 client
s3_client = boto3.client('s3')

# Get the S3 bucket name from environment variables set in SAM template
SOURCE_BUCKET_NAME = os.environ.get('SOURCE_BUCKET_NAME')

def lambda_handler(event, context):
    """
    AWS Lambda function to generate a presigned S3 URL for file uploads.
    This function is triggered by an API Gateway POST request.
    It returns a presigned URL that the frontend can use to directly upload a file to S3.
    """
    
    print(f"Received event: {json.dumps(event)}")

    # Define CORS headers for the API Gateway response.
    # This is crucial for web browsers to allow requests from your frontend.
    cors_headers = {
        "Access-Control-Allow-Origin": "*",  # Allows access from any origin
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Methods": "POST,OPTIONS,PUT" # Include PUT for the actual S3 upload
    }

    # Handle OPTIONS requests (CORS preflight)
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': ''
        }

    # Process POST requests for generating the presigned URL
    elif event['httpMethod'] == 'POST':
        try:
            body = json.loads(event['body'])
            file_name = body.get('fileName')
            file_type = body.get('fileType')
            user_email = body.get('userEmail') # Get user email to associate with the file

            if not file_name or not file_type or not user_email:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'message': 'Missing fileName, fileType, or userEmail in request body.'})
                }

            # Generate a unique key for the S3 object to prevent overwrites and organize files.
            # Using a UUID ensures uniqueness. We can also include user_email in the prefix for organization.
            object_key = f"{user_email}/{uuid.uuid4()}-{file_name}"

            # Generate the presigned URL for PUT operation.
            # The 'ExpiresIn' parameter defines how long the URL is valid (e.g., 3600 seconds = 1 hour).
            presigned_url = s3_client.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket': SOURCE_BUCKET_NAME,
                    'Key': object_key,
                    'ContentType': file_type,
                    # Add metadata to the S3 object to store user_email for later retrieval.
                    # This is crucial for the email_reply_processor_lambda to know who to email.
                    'Metadata': {
                        'x-amz-meta-user-email': user_email
                    }
                },
                ExpiresIn=3600 # URL valid for 1 hour
            )

            print(f"Generated presigned URL for {object_key}")

            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'uploadUrl': presigned_url,
                    'key': object_key # Return the S3 key as well for reference
                })
            }

        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return {
                'statusCode': 500,
                'headers': cors_headers,
                'body': json.dumps({'message': f'Internal server error: {str(e)}'})
            }
    
    else:
        return {
            'statusCode': 405,
            'headers': cors_headers,
            'body': json.dumps({'message': 'Method Not Allowed'})
        }
