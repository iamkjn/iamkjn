# EC2 Monitoring & IAM Access Management
## Project Overview:
This project demonstrates critical operational aspects of managing an AWS environment: proactive monitoring of EC2 instance health using CloudWatch alarms and securely managing access to AWS resources through IAM Groups and Users. It provides a foundational setup for maintaining system performance and adhering to the principle of least privilege.

## Problem Statement:
In a production environment like Heaven Classics, ensuring the optimal performance and availability of compute instances (EC2) is paramount. Manual monitoring is inefficient and reactive. Furthermore, providing appropriate access to AWS resources for different employees is crucial for security and operational efficiency. Heaven Classics needs an automated way to monitor their Windows 2012 Server EC2 instance's CPU utilization and receive immediate alerts for potential issues, while also establishing a secure user access framework.

### Architectural Solution:
The solution leverages AWS's core compute, monitoring, and identity management services:

### EC2 Instance (Windows Server 2022):

### An Amazon EC2 instance is launched, configured with a Windows Server 2022 R2 AMI. This instance represents a critical application server.

Detailed Monitoring is enabled for this EC2 instance, which sends CPU utilization data (and other standard metrics) to CloudWatch at 1-minute intervals.

### CloudWatch Alarm for CPU Utilization:

Amazon CloudWatch automatically collects standard metrics from the EC2 instance, including CPUUtilization.

A CloudWatch Alarm is configured to monitor the CPUUtilization metric.

This alarm is set to trigger if the average CPU utilization for the EC2 instance falls below a specified threshold (e.g., 3%) for a consecutive period (e.g., three consecutive 5-minute periods).

When the alarm state changes to ALARM (low CPU), it sends a notification.

### SNS Topic for Notifications:

An Amazon Simple Notification Service (SNS) Topic is created to act as a central notification channel.

The CloudWatch Alarm is configured to publish messages to this SNS Topic when it enters the ALARM state.

An email subscription is set up for the SNS Topic, ensuring that HCMonitor@HeavenClassics.com receives an email notification when the CPU utilization drops.

### IAM Group (Administrator Group):

AWS Identity and Access Management (IAM) is used to define fine-grained access control.

An IAM Group named Administrator Group is created.

The AWS managed policy AdministratorAccess is attached to this group, granting its members full administrative permissions across the AWS account.

### IAM User:

An IAM User is created for an employee (e.g., heavenclassics-admin-user).

This user is then added to the Administrator Group, inheriting all permissions granted to that group.

### Automated Deployment (AWS Serverless Application Model - SAM):

The entire infrastructure (EC2 Instance, CloudWatch Alarm, SNS Topic, IAM Group, and IAM User) is defined and deployed using an AWS SAM template (template.yaml). This ensures consistent, repeatable, and version-controlled deployments.

### Key Architectural Decisions (KADs):
AWS CloudWatch for Monitoring: Chosen as the native AWS monitoring solution due to its seamless integration with EC2, ability to collect standard and custom metrics, and robust alarming capabilities.

SNS for Notifications: Utilized as a flexible and scalable messaging service to deliver alarm notifications via email, allowing for easy integration with various subscription endpoints in the future.

IAM Groups for Permission Management: Implemented to simplify permission management. Instead of attaching policies directly to individual users, users are added to groups, and permissions are managed at the group level, promoting consistency and reducing administrative overhead.

Managed AdministratorAccess Policy: Used for the Administrator Group to quickly grant comprehensive access, suitable for a core administrative role. In a real-world scenario, custom policies with more granular permissions would be preferred for specific roles to adhere to the principle of least privilege.

Infrastructure as Code (AWS SAM): All resources are defined in template.yaml to ensure automated, repeatable deployments, version control, and traceability of infrastructure changes.

### Diagrams:
Architectural diagrams for this project would typically include:

System Context Diagram (C4 Model Level 1): Showing the monitoring team and the AWS Cloud.

Container Diagram (C4 Model Level 2): Detailing the EC2 instance, CloudWatch, SNS, and IAM components, illustrating the flow of metrics and alarms, and the IAM access model.

Activity Diagram: Illustrating the process of CPU utilization dropping, alarm triggering, and email notification.

(You would place your actual diagram image files in the diagrams/ folder.)

### Outcomes & Benefits:
This project successfully demonstrates the implementation of a foundational AWS operational setup, providing:

Proactive Monitoring: Ensures critical infrastructure issues (like low CPU utilization indicating an idle or hung server) are detected and alerted immediately, preventing service disruptions.

Centralized Notification: Provides a unified channel for alerts, making it easy to manage and distribute notifications.

Secure Access Management: Establishes a clear and manageable structure for controlling access to the AWS account, enhancing security posture.

Operational Efficiency: Automates monitoring and user provisioning, reducing manual effort and potential for human error.

Compliance Readiness: Lays the groundwork for auditing and compliance by defining user permissions systematically.

This solution is crucial for any organization aiming to maintain a healthy, secure, and well-managed AWS environment.