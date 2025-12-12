# TechCommerce DevOps Infrastructure

## A complete DevOps implementation of a microservices-based e-commerce platform. This project demonstrates containerization, orchestration, CI/CD, tunneling, centralized logging, and infrastructure as code (IaC) using Kubernetes, GitHub Actions, ngrok, Loki, and Terraform.

## Table of Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [CI/CD Pipeline](#cicd-pipeline)
- [Tunneling](#tunneling)
- [Logging](#logging)
- [Infrastructure as Code](#infrastructure-as-code)
- [Design Decisions & Security](#design-decisions--security)
- [Troubleshooting](#troubleshooting)
- [Demonstration](#demonstration)

---

## Overview

TechCommerce is a microservices-based e-commerce solution deployed on a Kubernetes cluster.
It includes three independent services:

- **Frontend:** Node.js (port 3000)
- **Product API:** Python Flask (port 5000)
- **Order API:** Python Flask (port 8000)

This project integrates DevOps practices such as CI/CD pipelines, automated testing, image scanning, monitoring, tunneling, centralized logging, and IaC.

---

- **HPA:** Product API scales 2–10 pods based on 70% CPU
- **Health checks:** Liveness and readiness probes for all services

**Benefits of Microservices:**

| Monolith               | Microservices               |
| ---------------------- | --------------------------- |
| Single large app       | Independent services        |
| One failure breaks all | Fault isolation             |
| Hard to scale features | Scale services individually |
| Hard to update         | Easy independent updates    |

---

## Technology Stack

**Application Layer**

- Frontend: Node.js, Express, Jest
- APIs: Python Flask, Pytest

**DevOps and Infrastructure**

- Docker
- Kubernetes (Minikube)
- GitHub Actions for CI/CD
- Trivy and Semgrep for security scanning
- ngrok for tunneling
- Loki and Promtail for logging
- Terraform for IaC
- Prometheus and Grafana (from midterm)

- Docker Hub (image registry)

Note:
For this assignment, staging and production deployments are mocked using echo commands to simulate Kubernetes rollouts. This preserves the full CI/CD flow without requiring live cluster access or real Docker credentials.

**Monitoring**

- Prometheus (metrics collection)
- Grafana (visualization)
- Alert Manager (alerts)

---

## Quick Start

### Prerequisites

- Docker Desktop
- Minikube
- kubectl
- Terraform
- ngrok account

### Local Development

```bash
git clone https://github.com/mnafisa100/devops-midterm-2025.git
cd devops-midterm-2025
minikube start
```

# Deploy Kubernetes resources

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/
```

# Forward ports

```bash
kubectl port-forward svc/frontend 3000:3000 -n techcommerce
kubectl port-forward svc/product-api 5000:5000 -n techcommerce
kubectl port-forward svc/order-api 8000:8000 -n techcommerce
```

## Monitoring

Deploy the monitoring stack:

```bash
kubectl apply -f k8s/monitoring/
kubectl port-forward svc/grafana 3001:3000 -n monitoring
```

## Access Grafana

- URL: [http://localhost:3001](http://localhost:3001)
- Default login: `admin/admin`

## Build and Load Images

```bash
docker build -t techcommerce/frontend:latest services/frontend/
docker build -t techcommerce/product-api:latest services/product-api/
docker build -t techcommerce/order-api:latest services/order-api/

minikube image load techcommerce/frontend:latest
minikube image load techcommerce/product-api:latest
minikube image load techcommerce/order-api:latest

```

---

## CI/CD Pipeline

**Stages:**

| Stage               | Description                                   |
| ------------------- | --------------------------------------------- |
| Test                | Run automated tests for frontend and APIs     |
| Security Scan       | Semgrep scans code for vulnerabilities        |
| Build Docker Images | Multi-stage builds, push to Docker Hub        |
| Scan Docker Images  | Trivy vulnerability scan                      |
| Deploy Staging      | Automatic deployment to staging environment   |
| Manual Approval     | Approval required before production           |
| Deploy Production   | Deploy to production with rollback on failure |

---

## Tunneling

Tunneling provides public access to local Kubernetes services using ngrok.
Steps to set up tunneling:

- Obtain an ngrok auth token.
- Add it to `ngrok.yml`.
- Start tunnels:

```bash
./start-tunnels-simple.sh
```

- Retrieve tunnel URLs:

```bash
./get-tunnel-urls.sh
```

- Access the application through the generated public URLs.
- Stop tunnels using:

```bash
./stop-tunnels.sh
```

---

## Logging

Centralized logging is implemented using Loki and Promtail.

How It Works
Pod stdout → Promtail → Loki → Query API or Grafana

Deployment

```bash
kubectl apply -f k8s/logging/loki-stack.yaml
kubectl get pods -n logging
```

Query Logs

```bash
kubectl port-forward svc/loki 3100:3100 -n logging

curl -G 'http://localhost:3100/loki/api/v1/query' \
--data-urlencode 'query={namespace="techcommerce"}'
```

---

## Infrastructure as Code

Terraform is used to define and manage Kubernetes resources.

Usage

```bash
cd terraform

terraform init
terraform plan
terraform apply
```

Terraform allows reproducible deployments and version-controlled infrastructure definitions.

## Design Decisions & Security

- **Multi-stage Docker builds:** smaller, secure images
- **Health checks:** ensures reliability and zero-downtime deployments
- **Horizontal Pod Autoscaler (HPA):** auto-scale Product API based on CPU
- **ConfigMaps & Secrets:** separate config from sensitive data
- **Resource limits:** prevent resource hogging and improve scheduling
- **Network policies:** restrict service-to-service communication
- **Security:** non-root containers, read-only filesystem, RBAC, encrypted secrets, Trivy scans

---

## Troubleshooting

### CrashLoopBackOff

**Steps:**

1. **Check pod logs**

```bash
kubectl logs <pod-name> -n techcommerce
```

# Check Events

To see recent Kubernetes events for troubleshooting:

```bash
kubectl get events -n techcommerce
```

### Slow Application (Normal CPU/Memory)

**Steps:**

- Profile the application code
- Check database queries, external API calls, and caching
- Adjust connection pools or fix memory leaks

### ImagePullBackOff

**Steps:**

- Verify image name and tag
- Check registry credentials and network connectivity
- Use `imagePullSecrets` for private repositories

## Demonstration

Local Access

```bash
kubectl port-forward svc/frontend 3000:3000 -n techcommerce
kubectl port-forward svc/product-api 5000:5000 -n techcommerce
kubectl port-forward svc/order-api 8000:8000 -n techcommerce
```

Public Access via ngrok

- Start tunnels
- Retrieve URLs
- Access services

View Logs:

```bash
kubectl logs -n techcommerce -l app=frontend
```

Loji Logs:

```bash
kubectl port-forward svc/loki 3100:3100 -n logging
curl 'http://localhost:3100/loki/api/v1/query?query={namespace="techcommerce"}'
```
