import json
import os
import boto3
from datetime import datetime
import base64 # Import base64 for encoding/decoding S3 object keys

# Initialize S3 and SES clients
s3_client = boto3.client('s3')
ses_client = boto3.client('ses')

# Get environment variables from SAM template
SENDER_EMAIL = os.environ.get('SENDER_EMAIL') # Verified email address for sending notifications
# DELETION_DOMAIN is not directly used in this lambda, but passed for consistency if needed later.
# DELETION_DOMAIN = os.environ.get('DELETION_DOMAIN') 

def lambda_handler(event, context):
    """
    AWS Lambda function triggered by S3 ObjectCreated event.
    It processes the uploaded file details and sends an email notification to the user.
    """
    
    print(f"Received S3 event: {json.dumps(event)}")

    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        file_size = record['s3']['object']['size']

        print(f"Processing file: {object_key} from bucket: {bucket_name}")

        try:
            # 1. Retrieve file metadata to get the user's email.
            # The user_email was stored as metadata during the presigned URL generation.
            response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
            user_email = response['Metadata'].get('x-amz-meta-user-email')

            if not user_email:
                print(f"Warning: User email metadata not found for {object_key}. Skipping email notification.")
                continue # Skip to the next record if email is missing

            # 2. Prepare email content.
            # The email subject needs a unique identifier for later deletion.
            # We'll use the S3 object key, base64 encoded to avoid issues with special characters in subject lines.
            encoded_object_key = base64.b64encode(object_key.encode('utf-8')).decode('utf-8')
            
            subject = f"File Uploaded: {os.path.basename(object_key)} - ID:{encoded_object_key}"
            body_text = f"""
Dear User,

Your file "{os.path.basename(object_key)}" (Size: {file_size} bytes) has been successfully uploaded to the cloud.

File Path: s3://{bucket_name}/{object_key}
Uploaded At: {datetime.now().isoformat()}

If you wish to delete this file, please reply to this email with the word "Delete" (case-insensitive) in the subject or body.
Please ensure your reply is sent from this email address ({user_email}).

Thank you,
Your Cloud Automation Team
"""
            # HTML body for a nicer email format
            body_html = f"""
<html>
<head></head>
<body>
  <p>Dear User,</p>
  <p>Your file "<b>{os.path.basename(object_key)}</b>" (Size: {file_size} bytes) has been successfully uploaded to the cloud.</p>
  <p><b>File Path:</b> s3://{bucket_name}/{object_key}</p>
  <p><b>Uploaded At:</b> {datetime.now().isoformat()}</p>
  <p>If you wish to delete this file, please reply to this email with the word "<b>Delete</b>" (case-insensitive) in the subject or body.</p>
  <p>Please ensure your reply is sent from this email address (<code>{user_email}</code>).</p>
  <p>Thank you,<br>Your Cloud Automation Team</p>
</body>
</html>
"""

            # 3. Send email using SES.
            ses_client.send_email(
                Source=SENDER_EMAIL,
                Destination={'ToAddresses': [user_email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {
                        'Text': {'Data': body_text},
                        'Html': {'Data': body_html}
                    }
                }
            )
            print(f"Notification email sent to {user_email} for file {object_key}.")

        except Exception as e:
            print(f"Error processing {object_key} or sending email: {e}")
            # In a real application, you might want to log this to a dead-letter queue
            # or trigger an alert for failed processing.

    return {
        'statusCode': 200,
        'body': json.dumps('File processing and notification complete.')
    }
