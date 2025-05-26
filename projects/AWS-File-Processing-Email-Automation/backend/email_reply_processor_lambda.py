import json
import os
import boto3
import base64
import re # For regular expressions to parse email content
from email import message_from_string # To parse raw email content
from email.iterators import _structure # Helper for email parsing

# Initialize S3 and SES clients
s3_client = boto3.client('s3')
ses_client = boto3.client('ses')

# Get environment variables from SAM template
SOURCE_BUCKET_NAME = os.environ.get('SOURCE_BUCKET_NAME')
DELETED_BUCKET_NAME = os.environ.get('DELETED_BUCKET_NAME')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL') # Verified email address for sending confirmations

def get_email_body(raw_email_content):
    """
    Parses the raw email content to extract the plain text or HTML body.
    Prioritizes plain text if available.
    """
    msg = message_from_string(raw_email_content)
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # Look for plain text first
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True).decode('utf-8')
                break # Prefer plain text
            # Fallback to HTML if no plain text
            elif ctype == 'text/html' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True).decode('utf-8')
    else:
        # Not a multipart email, just get the payload
        body = msg.get_payload(decode=True).decode('utf-8')
    return body


def lambda_handler(event, context):
    """
    AWS Lambda function triggered by SQS messages containing email replies.
    It parses the email, checks for a 'Delete' command, and moves the corresponding file in S3.
    """
    
    print(f"Received SQS event: {json.dumps(event)}")

    for record in event['Records']:
        try:
            # SQS message body contains the full SES email notification JSON
            ses_notification = json.loads(record['body'])
            mail_data = ses_notification['mail']
            message_id = mail_data['messageId']
            sender_email = mail_data['source']
            subject = mail_data['commonHeaders']['subject']
            
            # Get the raw email content from S3 (as specified in SES receipt rule action)
            # The SQS message contains the S3 bucket and object key where the raw email is stored.
            s3_object_key_raw_email = ses_notification['receipt']['action']['objectKey']
            s3_bucket_name_raw_email = ses_notification['receipt']['action']['bucketName']

            print(f"Processing email {message_id} from {sender_email} with subject: {subject}")
            print(f"Raw email stored in s3://{s3_bucket_name_raw_email}/{s3_object_key_raw_email}")

            # Retrieve the raw email content from S3
            raw_email_object = s3_client.get_object(Bucket=s3_bucket_name_raw_email, Key=s3_object_key_raw_email)
            raw_email_content = raw_email_object['Body'].read().decode('utf-8')
            
            # Extract the email body
            email_body = get_email_body(raw_email_content)
            print(f"Email body extracted (first 200 chars): {email_body[:200]}...")

            # Check if the email contains the "Delete" command (case-insensitive)
            # We'll check both subject and extracted body for the keyword.
            delete_command_found = False
            if re.search(r'\bdelete\b', subject, re.IGNORECASE):
                delete_command_found = True
            elif re.search(r'\bdelete\b', email_body, re.IGNORECASE):
                delete_command_found = True

            if delete_command_found:
                print(f"'Delete' command found in email {message_id}. Attempting to identify and move file.")
                
                # Extract the original file's S3 object key from the subject.
                # This requires careful parsing of the subject line format used by file_processor_notifier_lambda.
                # Example subject: "File Uploaded: my_document.pdf - ID:bXlfdGhpbmdzL3V1aWQtbXlfZG9jdW1lbnQucGRm"
                match = re.search(r'ID:([a-zA-Z0-9=\-]+)', subject)
                if match:
                    encoded_original_key = match.group(1)
                    try:
                        original_s3_key = base64.b64decode(encoded_original_key).decode('utf-8')
                        print(f"Identified original S3 key: {original_s3_key}")

                        # Move the file from source to deleted bucket
                        copy_source = {'Bucket': SOURCE_BUCKET_NAME, 'Key': original_s3_key}
                        
                        # Copy the file to the deleted bucket
                        s3_client.copy_object(
                            CopySource=copy_source,
                            Bucket=DELETED_BUCKET_NAME,
                            Key=original_s3_key # Keep the same key in the deleted bucket
                        )
                        # Delete the file from the source bucket
                        s3_client.delete_object(Bucket=SOURCE_BUCKET_NAME, Key=original_s3_key)
                        
                        print(f"File '{original_s3_key}' moved from '{SOURCE_BUCKET_NAME}' to '{DELETED_BUCKET_NAME}'.")
                        
                        # Send confirmation email
                        ses_client.send_email(
                            Source=SENDER_EMAIL,
                            Destination={'ToAddresses': [sender_email]},
                            Message={
                                'Subject': {'Data': f"Confirmation: File '{os.path.basename(original_s3_key)}' Deleted"},
                                'Body': {'Text': {'Data': f"Your file '{os.path.basename(original_s3_key)}' has been successfully moved to the deleted items folder. It is no longer in active storage."}}
                            }
                        )
                        print(f"Deletion confirmation email sent to {sender_email}.")
                    except Exception as decode_error:
                        print(f"Error decoding original S3 key from base64: {decode_error}. Encoded key: {encoded_original_key}")
                        # Send error email to user if decoding fails
                        ses_client.send_email(
                            Source=SENDER_EMAIL,
                            Destination={'ToAddresses': [sender_email]},
                            Message={
                                'Subject': {'Data': f"Action Failed: Could Not Process Your Delete Request"},
                                'Body': {'Text': {'Data': f"Dear user, we received your delete request, but encountered an issue identifying the file. Please ensure you are replying to an original notification email without altering the subject line's ID. If the issue persists, contact support."}}
                            }
                        )
                else:
                    print(f"Could not extract original S3 key ID from subject: {subject}. Skipping file deletion.")
                    ses_client.send_email(
                        Source=SENDER_EMAIL,
                        Destination={'ToAddresses': [sender_email]},
                        Message={
                            'Subject': {'Data': f"Action Failed: Could Not Process Your Delete Request"},
                            'Body': {'Text': {'Data': f"Dear user, we received your delete request, but we could not identify the file from the email subject. Please ensure you are replying to an original notification email without altering the subject line. If the issue persists, contact support."}}
                        }
                    )
            else:
                print(f"No 'Delete' command found in email {message_id}. No action taken.")

        except Exception as e:
            print(f"Error processing SQS record or email: {e}")
            # In a real system, you might send a notification about the processing failure
            # or move the SQS message to a Dead-Letter Queue.

    return {
        'statusCode': 200,
        'body': json.dumps('Email reply processing complete.')
    }
