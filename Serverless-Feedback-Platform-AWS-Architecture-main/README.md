# Serverless Feedback Website
### Project Overview:
This project demonstrates the implementation of a fully serverless feedback collection website using Amazon Web Services (AWS). It provides a secure, scalable, and cost-effective solution for businesses to gather and store customer feedback.

### Problem Statement:
Traditional methods of collecting customer feedback often involve managing dedicated servers, databases, and complex authentication systems. This leads to increased operational overhead, scaling challenges, and higher costs, diverting resources from core business activities. A solution was needed that could efficiently capture feedback without the need for constant infrastructure management.

## Architecture Diagram

![Architecture Diagram](diagram/architecture-diagram.png)

### Architectural Solution:
The solution leverages a combination of serverless AWS services to create a highly available and scalable feedback platform.

### Frontend (Static Website on S3):

The user-facing feedback form, built with HTML, CSS, and JavaScript, is hosted directly on an AWS S3 bucket configured for static website hosting. S3 provides high availability, scalability, and security for delivering static content globally.

The JavaScript within the frontend handles the submission of feedback data to the backend API.

### Backend (API Gateway, Lambda, DynamoDB):

Amazon API Gateway acts as the secure entry point for feedback submissions. It exposes a RESTful endpoint that the frontend calls. API Gateway manages request routing, throttling, and basic security measures.

An AWS Lambda function is triggered by API Gateway. This function processes the incoming feedback, performs any necessary validation, generates a unique ID, and orchestrates its storage.

Amazon DynamoDB, a fully managed NoSQL database, stores the feedback entries. Its serverless nature ensures automatic scaling to handle varying loads and provides fast, predictable performance without database administration.

### Security (IAM):

AWS Identity and Access Management (IAM) roles and policies are meticulously configured using AWS Serverless Application Model (SAM). This ensures that the Lambda function has only the necessary permissions to interact with DynamoDB (e.g., PutItem) and that API Gateway can invoke the Lambda function, adhering to the principle of least privilege.

### Key Architectural Decisions (KADs):
Serverless-First Approach: Chosen to minimize operational overhead, reduce costs (pay-as-you-go), and enable automatic scalability without manual intervention.

Static Website Hosting on S3: Opted for S3 due to its inherent high availability, scalability, and cost-effectiveness for static content delivery, eliminating the need for web servers.

DynamoDB for Feedback Storage: Selected for its serverless, NoSQL nature, offering seamless scalability and high performance for key-value data storage, perfect for individual feedback entries.

API Gateway for Backend Exposure: Utilized to provide a secure, scalable, and managed interface for the frontend to interact with the Lambda function, handling the complexities of web connectivity.

AWS SAM for Deployment: Chosen to define and deploy the serverless application's resources (Lambda, API Gateway, DynamoDB) in a single, version-controlled template, promoting automation and consistency.

### Diagrams:
Architectural diagrams for this project would typically include:

System Context Diagram (C4 Model Level 1): Showing the user interacting with the Serverless Feedback Website system.

Container Diagram (C4 Model Level 2): Detailing the S3 bucket (frontend), API Gateway, Lambda function, and DynamoDB table as "containers" of code or data.

Deployment Diagram: Illustrating how these AWS services are deployed and interact within the AWS cloud environment.

(You would place your actual diagram image files in the diagrams/ folder.)

### Code Examples:
Illustrative code snippets for the frontend, backend Lambda function, and the AWS SAM template for infrastructure provisioning are provided in their respective folders:

frontend/: HTML, CSS, and JavaScript for the feedback form.

backend/: Python code for the AWS Lambda function.

infrastructure/: AWS SAM template (template.yaml) for deploying the AWS resources.

### Outcomes & Benefits:
This project successfully demonstrates a highly scalable, cost-effective, and easy-to-manage solution for collecting and analyzing customer feedback. The serverless architecture ensures:

Scalability: Automatically handles varying loads from a few submissions to millions without manual scaling.

Cost-Effectiveness: Only pay for the compute time and storage consumed, significantly reducing operational costs.

Reduced Management Overhead: No servers to provision, patch, or maintain, allowing focus on application logic.

Faster Development: Accelerates deployment by abstracting away infrastructure concerns.

This approach empowers businesses to focus on improving their products and services based on valuable customer insights, rather than managing complex infrastructure.

### Why Work With Me?
I deliver architectural solutions that bridge technical vision with business goals, enabling organizations to innovate faster and operate more efficiently. My focus is on creating architectures that are not only powerful today but are also adaptable for the challenges of tomorrow.

### Contact:
Feel free to connect with me to discuss architectural challenges or opportunities:

LinkedIn: [https://www.linkedin.com/in/krunalnayak]

Email: [Krunalnayak49@gmail.com]
