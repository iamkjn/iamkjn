document.addEventListener('DOMContentLoaded', () => {
    // Get references to the form, input elements, and message display
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const userEmailInput = document.getElementById('userEmail');
    const messageDiv = document.getElementById('message');

    // **IMPORTANT**: Replace with your actual API Gateway endpoint URL for generating presigned URLs.
    // This URL will be an output from your SAM deployment of the 'UploadUrlGeneratorLambda'.
    const PRESIGNED_URL_API_ENDPOINT = 'YOUR_PRESIGNED_URL_API_ENDPOINT_HERE';

    // Add an event listener for the form submission
    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission (page reload)

        const file = fileInput.files[0]; // Get the selected file
        const userEmail = userEmailInput.value; // Get the user's email

        // Basic client-side validation
        if (!file) {
            showMessage('Please select a file to upload.', 'error');
            return;
        }
        if (!userEmail) {
            showMessage('Please enter your email address for notification.', 'error');
            return;
        }

        showMessage('Requesting upload URL...', 'info');

        try {
            // 1. Request a presigned URL from the API Gateway endpoint
            const getPresignedUrlResponse = await fetch(PRESIGNED_URL_API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    fileName: file.name,
                    fileType: file.type,
                    userEmail: userEmail // Pass user email so Lambda can associate it
                }),
            });

            if (!getPresignedUrlResponse.ok) {
                const errorData = await getPresignedUrlResponse.json();
                throw new Error(`Failed to get presigned URL: ${errorData.message || getPresignedUrlResponse.statusText}`);
            }

            const { uploadUrl, key } = await getPresignedUrlResponse.json(); // Destructure the response

            showMessage(`Uploading "${file.name}"...`, 'info');

            // 2. Upload the file directly to S3 using the presigned URL
            const uploadToS3Response = await fetch(uploadUrl, {
                method: 'PUT', // Use PUT for direct S3 upload
                headers: {
                    'Content-Type': file.type, // Set content type to match the file
                },
                body: file, // Send the file data directly
            });

            if (uploadToS3Response.ok) {
                showMessage(`File "${file.name}" uploaded successfully! You will receive an email notification shortly.`, 'success');
                uploadForm.reset(); // Reset the form
            } else {
                const errorText = await uploadToS3Response.text();
                throw new Error(`Failed to upload file to S3: ${uploadToS3Response.status} - ${errorText}`);
            }

        } catch (error) {
            console.error('Upload process failed:', error);
            showMessage(`Upload failed: ${error.message}`, 'error');
        }
    });

    /**
     * Displays a message in the messageDiv.
     * @param {string} text - The message text to display.
     * @param {string} type - The type of message ('success', 'error', 'info').
     */
    function showMessage(text, type) {
        messageDiv.textContent = text;
        messageDiv.className = `message ${type} block`; // Apply CSS classes and make visible
        messageDiv.style.display = 'block'; // Ensure it's displayed

        // Hide message automatically after a few seconds, unless it's an error
        if (type !== 'error') {
            setTimeout(() => {
                messageDiv.style.display = 'none';
                messageDiv.textContent = '';
                messageDiv.className = 'message hidden';
            }, 7000); // Message disappears after 7 seconds
        }
    }
});
