# Video to MP3 Converter Microservice

A cloud-native microservices application that converts video files to MP3 format, built with modern technologies and cloud-native principles. The project demonstrates expertise in distributed systems, containerization, and cloud architecture.

## Technical Highlights

-   **Microservices Architecture** using Python and Flask
-   **Container Orchestration** with Kubernetes
-   **Message Queue System** using RabbitMQ for asynchronous processing
-   **Authentication** implemented with JWT tokens
-   **Database Systems**:
    -   MongoDB with GridFS for file storage
    -   MySQL for user management
-   **Infrastructure as Code** using Kubernetes manifests
-   **RESTful API Design** principles
-   **DevOps Practices**:
    -   Docker containerization
    -   Kubernetes deployment configurations
    -   Service discovery and load balancing

## Key Features

-   Secure user authentication and authorization
-   Asynchronous video processing using message queues
-   Scalable file storage using MongoDB GridFS
-   Email notifications upon completion
-   Containerized microservices for easy scaling
-   High availability through Kubernetes deployments

## System Architecture

The system consists of four independent microservices:

-   **Gateway Service**: API gateway handling client requests and file operations
-   **Auth Service**: Manages user authentication and JWT token validation
-   **Converter Service**: Handles video to MP3 conversion using MoviePy
-   **Notification Service**: Sends email notifications to users

## Technologies Used

-   **Backend**: Python, Flask
-   **Databases**: MongoDB, MySQL
-   **Message Broker**: RabbitMQ
-   **Containerization**: Docker
-   **Orchestration**: Kubernetes
-   **API Security**: JWT Authentication
-   **File Processing**: MoviePy, GridFS
