# TechCommerce DevOps Infrastructure

CI/CD pipeline and Kubernetes deployment for a microservices e-commerce platform

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [CI/CD Pipeline](#cicd-pipeline)
- [Design Decisions & Security](#design-decisions--security)
- [Monitoring & Alerts](#monitoring--alerts)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

TechCommerce is an e-commerce platform split into three microservices:

- **Frontend:** Node.js (port 3000)
- **Product API:** Python Flask (port 5000)
- **Order API:** Python Flask (port 8000)

Features include automated CI/CD, Docker/Kubernetes deployment, security scanning, auto-scaling, and monitoring with alerts. Microservices allow independent updates, scaling, and fault isolation.

---

## Architecture

User Browser
│
▼
Frontend Service
│
┌────┴────┐
▼ ▼
Product API Order API

yaml
Copy code

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

**Container & Orchestration**

- Docker (multi-stage builds)
- Kubernetes, Minikube

**CI/CD Pipeline**

- GitHub Actions
- Semgrep (code scanning)
- Trivy (image scanning)
- Docker Hub (image registry)

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
- GitHub account

### Local Development

```bash
git clone https://github.com/mnafisa100/devops-midterm-2025.git
cd devops-midterm-2025
minikube start
```

# Deploy Kubernetes resources

kubectl apply -f k8s/

# Forward ports

kubectl port-forward svc/frontend 3000:3000 -n techcommerce
kubectl port-forward svc/product-api 5000:5000 -n techcommerce
kubectl port-forward svc/order-api 8000:8000 -n techcommerce

## Monitoring

Deploy the monitoring stack:

```bash
kubectl apply -f k8s/monitoring/
kubectl port-forward svc/grafana 3001:3000 -n monitoring
```

## Access Grafana

- URL: [http://localhost:3001](http://localhost:3001)
- Default login: `admin/admin`

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

## Design Decisions & Security

- **Multi-stage Docker builds:** smaller, secure images
- **Health checks:** ensures reliability and zero-downtime deployments
- **Horizontal Pod Autoscaler (HPA):** auto-scale Product API based on CPU
- **ConfigMaps & Secrets:** separate config from sensitive data
- **Resource limits:** prevent resource hogging and improve scheduling
- **Network policies:** restrict service-to-service communication
- **Security:** non-root containers, read-only filesystem, RBAC, encrypted secrets, Trivy scans

---

## Monitoring & Alerts

| Metric            | Threshold     | Action                       |
| ----------------- | ------------- | ---------------------------- |
| Pod restarts      | >3 in 10 min  | Investigate crashes          |
| API response time | >2s for 5 min | Check DB/API latency         |
| Error rate        | >5% for 5 min | Check application logs       |
| Disk usage        | >85%          | Clean logs or expand storage |

- Prometheus collects metrics
- Grafana visualizes dashboards
- Alert Manager notifies critical issues

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
