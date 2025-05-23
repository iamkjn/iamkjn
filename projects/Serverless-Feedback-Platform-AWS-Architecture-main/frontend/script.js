// Ensure the DOM is fully loaded before attaching event listeners
document.addEventListener('DOMContentLoaded', () => {
  // Get references to the form, message display, star rating elements, and hidden rating input
  const feedbackForm = document.getElementById('feedbackForm');
  const messageDiv = document.getElementById('message');
  const stars = document.querySelectorAll('.star-rating .star');
  const ratingInput = document.getElementById('rating');

  // **IMPORTANT**: Replace with your actual API Gateway endpoint URL.
  // This URL will be generated after deploying your API Gateway and Lambda function
  // using the provided AWS SAM template.
  // Example: 'https://xxxxxxxxxx.execute-api.eu-west-2.amazonaws.com/v1/feedback'
  const API_GATEWAY_ENDPOINT = 'https://ns6xv4xywg.execute-api.eu-west-2.amazonaws.com/assignment'; 

  // --- Star Rating Logic ---
  stars.forEach(star => {
      star.addEventListener('click', function () {
          const value = parseInt(this.dataset.value); // Get the star's data-value
          ratingInput.value = value; // Set the hidden input's value

          // Highlight selected stars
          stars.forEach(s => {
              if (parseInt(s.dataset.value) <= value) {
                  s.classList.add('selected'); // Add 'selected' class for gold color
              } else {
                  s.classList.remove('selected'); // Remove 'selected' class for unselected stars
              }
          });
      });
  });

  // --- Form Submission Logic ---
  // Attach an event listener to the form's submit event
  feedbackForm.addEventListener('submit', async (event) => {
      event.preventDefault(); // Prevent the default form submission behavior (page reload)

      // Gather form data
      const name = document.getElementById('name').value;
      const email = document.getElementById('email').value;
      const category = document.getElementById('category').value;
      const rating = parseInt(document.getElementById('rating').value); // Parse rating as integer
      const comment = document.getElementById('comment').value;

      // Basic client-side validation
      if (!comment.trim()) {
          showMessage('Please provide your feedback in the comment section.', 'error');
          return; // Stop submission if comment is empty
      }
      if (rating === 0) {
          showMessage('Please select a rating.', 'error');
          return; // Stop submission if rating is 0
      }

      // Construct the payload to send to the Lambda function via API Gateway
      // The Lambda expects a single JSON object with the feedback data.
      const feedbackData = {
          name: name,
          email: email,
          category: category,
          rating: rating,
          comment: comment
      };

      // Display a "submitting" message to the user
      showMessage('Submitting feedback...', 'info');

      try {
          // Send the feedback data to the API Gateway endpoint
          const response = await fetch(API_GATEWAY_ENDPOINT, {
              method: 'POST', // Use POST method to send data
              headers: {
                  'Content-Type': 'application/json', // Indicate that the request body is JSON
              },
              // The Lambda expects the actual JSON payload, not a stringified 'body' field.
              // So, directly stringify feedbackData.
              body: JSON.stringify(feedbackData), 
          });

          // Check if the response was successful (status code 2xx)
          if (response.ok) {
              const data = await response.json(); // Parse the JSON response from the backend
              if (data.success) {
                  showMessage('Feedback submitted successfully! Thank you!', 'success');
                  feedbackForm.reset(); // Clear the form fields after successful submission
                  // Reset star rating visually
                  stars.forEach(s => s.classList.remove('selected'));
                  ratingInput.value = 0; // Reset hidden rating value
              } else {
                  // Handle backend-specific errors returned in the 'error' field
                  showMessage(`Error: ${data.error || 'Something went wrong on the server.'}`, 'error');
              }
              console.log('API Response:', data); // Log the full API response for debugging
          } else {
              // If the response status is not OK (e.g., 400, 500)
              const errorText = await response.text(); // Get raw response text for debugging
              console.error('Error submitting feedback:', response.status, errorText);
              showMessage(`Error submitting feedback: ${response.status} - ${errorText || 'Please try again.'}`, 'error');
          }
      } catch (error) {
          // Catch any network errors or issues with the fetch request (e.g., CORS issues, API Gateway URL incorrect)
          console.error('Network or fetch error:', error);
          showMessage('Network error: Could not reach the server. Please check your connection or API Gateway URL.', 'error');
      }
  });

  /**
   * Displays a message in the messageDiv.
   * @param {string} text - The message text to display.
   * @param {string} type - The type of message ('success', 'error', 'info').
   */
  function showMessage(text, type) {
      messageDiv.textContent = text; // Set the message text
      messageDiv.className = `message ${type} block`; // Apply CSS class for styling and make it visible
      messageDiv.style.display = 'block'; // Ensure it's displayed

      // Automatically hide the message after a few seconds (optional, for non-error messages)
      if (type !== 'error') {
          setTimeout(() => {
              messageDiv.style.display = 'none';
              messageDiv.textContent = '';
              messageDiv.className = 'message hidden'; // Hide it again
          }, 5000); // Message disappears after 5 seconds
      }
  }
});
