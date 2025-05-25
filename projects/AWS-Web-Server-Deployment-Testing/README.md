# Web Server Deployment & Load Balancing for Client Website
## Project Overview:
This project demonstrates the end-to-end process of deploying a web server on AWS EC2, configuring a static website, creating a reusable Amazon Machine Image (AMI), and setting up an Application Load Balancer (ALB) to ensure high availability and successful testing of the web application.

## Problem Statement:
A new client requires a web server to host their website entirely on the AWS Cloud. After the initial web server setup, the critical next step is to ensure its high availability, scalability, and successful testing under various conditions. This involves not just launching a single instance, but creating a robust, load-balanced environment capable of handling traffic efficiently and reliably.

### Architectural Solution:
The solution involves a multi-step process to build a resilient web hosting environment:

Initial EC2 Instance Creation (Windows Server 2022):

An Amazon EC2 instance running Windows Server 2022 Base is launched.

User Data (PowerShell Script): A PowerShell script is executed during instance launch to automatically:

Install the IIS (Internet Information Services) web server role.

Create a simple static website (index.html) in the default IIS web root.

This initial instance serves as the "golden image" candidate.

### AMI Creation (Manual Step):

Once the initial EC2 instance is fully configured with IIS and the static website, a custom Amazon Machine Image (AMI) is created from this instance. This AMI captures the entire state of the configured server, including the OS, IIS, and the website content.

This AMI becomes the reusable template for launching identical, pre-configured web servers.

### Application Load Balancer (ALB):

An Application Load Balancer (ALB) is deployed across multiple Availability Zones. The ALB automatically distributes incoming application traffic across multiple targets, such as EC2 instances.

It operates at the application layer (Layer 7) and supports path-based routing, host-based routing, and SSL termination.

### Target Group:

A Target Group is created and associated with the ALB. This group registers the EC2 instances that will serve the web traffic.

Health checks are configured within the Target Group to continuously monitor the health of the registered instances (e.g., checking if IIS is responding on port 80).

### EC2 Instances from AMI (Managed by ASG - Conceptual for simplicity):

For this project, we will directly launch two new EC2 instances using the custom AMI created in step 2. (In a production scenario, these would typically be managed by an Auto Scaling Group for automatic scaling and healing).

These instances are registered with the ALB's Target Group.

### DNS Verification:

The DNS name of the Application Load Balancer is accessed via a web browser. The ALB distributes the request to one of the healthy EC2 instances, serving the static website. This verifies that the entire setup, from load balancer to web server, is functioning correctly.

### Key Architectural Decisions (KADs):
EC2 for Web Server Hosting: Provides full control over the operating system and web server software (IIS in this case).

IIS for Windows Web Server: A native and robust web server for Windows environments.

Custom AMI for Automation: Enables rapid and consistent deployment of pre-configured web servers, reducing manual setup time and ensuring uniformity across instances.

Application Load Balancer (ALB) for High Availability & Scalability: Provides load distribution, fault tolerance across Availability Zones, and improved performance by distributing traffic.

Static Website for Simple Testing: A basic index.html simplifies the verification process, confirming the web server is serving content.

Infrastructure as Code (AWS SAM): All foundational AWS resources (EC2, Security Groups, ALB, Target Group, Listener) are defined in template.yaml for automated, repeatable deployments.

### Diagrams:
Architectural diagrams for this project would typically include:

System Context Diagram (C4 Model Level 1): Showing the user interacting with the website hosted on AWS.

Container Diagram (C4 Model Level 2): Detailing the ALB, EC2 instances, and the flow of web traffic.

Deployment Diagram: Visualizing the deployment of EC2 instances across multiple Availability Zones behind the ALB.

(You would place your actual diagram image files in the diagrams/ folder.)

### Code Examples:
Illustrative code snippets for the static web content and the AWS SAM template for infrastructure provisioning are provided in their respective folders:

web-content/: Simple index.html file.

infrastructure/: AWS SAM template (template.yaml) for deploying the EC2 instance, ALB, and related resources.

### Outcomes & Benefits:
This project successfully demonstrates the deployment and testing of a highly available web server environment on AWS, providing:

High Availability: Traffic is distributed across multiple instances, ensuring the website remains accessible even if one instance fails.

Scalability: The architecture can easily scale horizontally by adding more EC2 instances behind the ALB.

Automated Configuration: User data scripts and AMIs streamline the server setup process.

Efficient Traffic Distribution: The ALB ensures optimal load balancing and health checking of web servers.

Robust Testing Environment: Provides a stable and verifiable setup for client website testing.

This solution is fundamental for hosting web applications that require reliability and performance on the AWS Cloud.