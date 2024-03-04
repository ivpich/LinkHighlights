# Videoconference Highlights Extractor

This project is designed to extract highlights from videoconference transcriptions, leveraging the power of OpenAI's tools. It's built with FastAPI and hosted with Uvicorn, providing a robust and fast API service. This README provides instructions on how to deploy the service both locally and on a Kubernetes cluster with a VPN sidecar container for secure access to OpenAI tools.

## Features

- Extract highlights from videoconference transcriptions.
- FastAPI for a fast and efficient API service.
- Dockerized application for easy deployment.
- Kubernetes deployment with VPN sidecar container for secure OpenAI tool access.

## Requirements

- Docker
- Kubernetes cluster (for Kubernetes deployment)
- kubectl (for Kubernetes deployment)
- Access to a VPN service (for Kubernetes deployment with VPN sidecar)

## Local Deployment

To deploy the highlights extractor locally using Docker:

1. Clone the repository:

```bash
git clone https://github.com/yourgithubusername/highlights-extractor.git
cd highlights-extractor
```

Build the Docker image:
```bash
docker build -t highlights-extractor.
```
Run the container:
```bash
docker run -d --name highlights-extractor -p 8000:8000 highlights-extractor
```
The API service is now running on http://localhost:8000.
Access the Swagger UI at http://localhost:8000/docs to explore the API endpoints.

Kubernetes Deployment
The Kubernetes deployment includes a VPN sidecar container to ensure secure access to OpenAI tools. Follow these steps to deploy the service on your Kubernetes cluster:

Apply the Kubernetes manifest:
```bash
kubectl apply -f deployment.yaml
```
This command deploys the highlights extractor service along with the VPN sidecar container configured for secure access to OpenAI tools.

To access the service, determine the external IP address or domain configured for your Ingress controller:
```bash
kubectl get ingress
```
Navigate to the provided IP address or domain in your browser to access the Swagger UI for the highlights extractor service.

Configuration
To configure the VPN sidecar container, modify the vpn-config section in the deployment.yaml file with your VPN configuration details.
Adjust the Dockerfile and Kubernetes manifest (deployment.yaml) as necessary to fit your deployment environment and requirements.


