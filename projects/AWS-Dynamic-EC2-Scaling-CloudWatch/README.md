# Dynamic EC2 Scaling with Auto Scaling & CloudWatch
## Project Overview:
This project demonstrates how to implement dynamic scaling for Amazon EC2 instances using AWS Auto Scaling and custom metrics published to Amazon CloudWatch. This architecture ensures that application compute capacity automatically adjusts to fluctuating demand, optimizing performance, user experience, and cost efficiency.

### Problem Statement:
Platforms like Hotstar or Amazon.com experience highly variable user traffic. Manually adding or removing servers (EC2 instances) to handle these fluctuations is inefficient, prone to errors, and costly due to over-provisioning during slack times or under-provisioning during peak loads, leading to poor customer satisfaction. On-premise solutions lack the elasticity to respond dynamically to demand.

The challenge is to automate the scaling of EC2 instances based on real-time application load, specifically using a custom metric like "number of users logged in" to ensure a jitter-free experience for customers and optimize resource utilization.

### Architectural Solution:
The solution leverages AWS's core compute, monitoring, and scaling services to create an elastic and responsive infrastructure:

EC2 Instances: These are the virtual servers that host the application.

CloudWatch Custom Metric:

A Python script (user_login_simulator.py) running on each EC2 instance simulates user activity and periodically publishes a custom metric (e.g., UsersLoggedIn) to Amazon CloudWatch.

Amazon CloudWatch collects and monitors these metrics, providing visibility into the application's load.

CloudWatch Alarms:

CloudWatch Alarms are configured to monitor the UsersLoggedIn custom metric.

When the metric crosses predefined thresholds (e.g., too many users, or very few users), these alarms are triggered.

Auto Scaling Group (ASG):

An AWS Auto Scaling Group (ASG) manages a collection of EC2 instances. It ensures that a specified number of instances are running and automatically replaces unhealthy instances.

The ASG uses a Launch Template to define how new EC2 instances should be configured (e.g., AMI, instance type, security groups, and user data for automated software installation and metric publishing).

Auto Scaling Policies:

Scaling Policies are attached to the ASG and linked to the CloudWatch Alarms.

When a "scale-out" alarm (e.g., UsersLoggedIn is high) is triggered, the policy instructs the ASG to launch more EC2 instances.

When a "scale-in" alarm (e.g., UsersLoggedIn is low) is triggered, the policy instructs the ASG to terminate instances.

IAM Roles:

AWS Identity and Access Management (IAM) roles are configured to grant the EC2 instances permission to publish custom metrics to CloudWatch.

Additional IAM roles are used by the Auto Scaling service to launch and terminate EC2 instances.

### Automated Deployment (AWS Serverless Application Model - SAM):

The entire infrastructure (EC2 Launch Template, Auto Scaling Group, CloudWatch Alarms, Auto Scaling Policies, and necessary IAM roles) is defined and deployed using an AWS SAM template (template.yaml). This ensures consistent, repeatable, and version-controlled deployments.

Key Architectural Decisions (KADs):
Auto Scaling for Elasticity: Chosen to automatically adjust compute capacity based on demand, ensuring optimal performance and cost efficiency.

CloudWatch Custom Metrics: Utilized to provide application-specific load indicators (e.g., UsersLoggedIn), enabling fine-grained control over scaling behavior that standard metrics might not offer.

Launch Templates with User Data: Employed to automate the bootstrapping process of new EC2 instances, including installing necessary software and starting the metric publishing script.

Target Tracking Scaling Policies (Conceptual): While the example uses simple step scaling for clarity, target tracking policies are a common, more advanced choice for maintaining a specific metric average.

AWS SAM for Infrastructure as Code: Utilized to define the entire scaling stack declaratively, enabling automated deployments and versioning of the infrastructure.

### Diagrams:
Architectural diagrams for this project would typically include:

System Context Diagram (C4 Model Level 1): Showing users interacting with the application, which is hosted on an Auto Scaling Group.

Container Diagram (C4 Model Level 2): Detailing the ASG, EC2 instances, CloudWatch, and the flow of metrics and scaling actions.

Sequence Diagram: Illustrating how user load increases, metrics are published, alarms trigger, and the ASG scales out.

Deployment Diagram: Visualizing the deployment of the ASG, EC2 instances, and CloudWatch within the AWS environment.

(You would place your actual diagram image files in the diagrams/ folder.)

### Code Examples:
Illustrative code snippets for simulating user logins and pushing metrics, and the AWS SAM template for infrastructure provisioning, are provided in their respective folders:

application-scripts/: Python script for user_login_simulator.py.

infrastructure/: AWS SAM template (template.yaml) for deploying the Auto Scaling setup.

Outcomes & Benefits:
This project successfully demonstrates a dynamic and highly responsive EC2 scaling solution on AWS, providing:

Optimized Performance: Ensures adequate compute resources are always available to handle current demand, leading to a smooth user experience.

Cost Efficiency: Automatically scales down during low demand, preventing wastage of CAPEX on under-utilized resources.

Increased Reliability: Automatically replaces unhealthy instances, maintaining application availability.

Reduced Manual Effort: Eliminates the need for manual intervention in scaling operations.

Business Agility: Allows businesses to respond quickly to market changes and unexpected traffic spikes.

This solution is fundamental for any organization building scalable and resilient applications on the AWS Cloud.