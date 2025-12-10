# 🚀 DevOps Infrastructure Guide

Complete guide for deploying AI News Analyzer with Docker, Kubernetes, and Terraform.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Docker Images](#docker-images)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Terraform Automation](#terraform-automation)
- [Monitoring \& Management](#monitoring--management)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

1. **Docker** (v20.10+)
   ```bash
   docker --version
   ```

2. **Kubernetes Cluster** (one of the following):
   - **Minikube** (local development)
     ```bash
     minikube start --cpus=4 --memory=8192
     ```
   - **Kind** (Kubernetes in Docker)
     ```bash
     kind create cluster --name ai-news
     ```
   - **Cloud Provider** (GKE, EKS, AKS)

3. **kubectl** (Kubernetes CLI)
   ```bash
   kubectl version --client
   ```

4. **Terraform** (v1.0+)
   ```bash
   terraform version
   ```

5. **DockerHub Account** (for image registry)

---

## Quick Start

### Option 1: Automated Deployment (Recommended)

Run the complete deployment script:

```bash
./scripts/deploy.sh
```

This script will:
1. Build Docker images
2. Push to DockerHub
3. Initialize Terraform
4. Deploy to Kubernetes

### Option 2: Manual Step-by-Step

Follow the detailed instructions below.

---

## 📝 Actual Deployment Logs (Automated)

Here are the logs from the automated deployment performed:

### 1. Cluster Setup
```bash
minikube delete && minikube start --cpus=4 --memory=8192 --driver=docker
# Output:
# * Deleting "minikube" in docker ...
# * Starting "minikube" primary control-plane node in "minikube" cluster
# * Done! kubectl is now configured to use "minikube" cluster
```

### 2. Backend Build (with djongo fix)
```bash
docker build -t mortadhajemai/ai-news-backend:latest ./backend
# Output:
# Successfully built djongo
# Successfully installed django-3.1.12 djongo-1.3.7 sqlparse-0.2.4
# Successfully built mortadhajemai/ai-news-backend:latest
```

### 3. Kubernetes Deployment
```bash
kubectl apply -f k8s/
# Output:
# configmap/backend-config created
# deployment.apps/backend created
# service/backend created
# deployment.apps/frontend created
# service/frontend created
# persistentvolumeclaim/mongodb-pvc created
# deployment.apps/mongodb created
# service/mongodb created
```

### 4. Pod Status
```bash
kubectl get pods -n ai-news-analyzer
# Output:
# NAME                        READY   STATUS    RESTARTS   AGE
# backend-86cbd9794c-7pb4j    0/1     Running   1          6m
# frontend-5f4445cfdb-2vrvh   1/1     Running   0          6m
# mongodb-6646864466-brj24    1/1     Running   0          6m
```

---

## Docker Images

### Images on DockerHub

- **Backend**: `mortadhajemai/ai-news-backend:latest`
- **Frontend**: `mortadhajemai/ai-news-frontend:latest`

### Build Locally

```bash
# Build backend
docker build -t mortadhajemai/ai-news-backend:latest ./backend

# Build frontend
docker build -t mortadhajemai/ai-news-frontend:latest ./frontend
```

### Push to DockerHub

```bash
# Login to DockerHub
docker login -u mortadhajemai

# Push images
docker push mortadhajemai/ai-news-backend:latest
docker push mortadhajemai/ai-news-frontend:latest
```

### Test Images Locally

```bash
# Run backend
docker run -p 8000:8000 mortadhajemai/ai-news-backend:latest

# Run frontend
docker run -p 80:80 mortadhajemai/ai-news-frontend:latest
```

---

## Kubernetes Deployment

### Method 1: Using kubectl (Manual)

```bash
# Apply all manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/mongodb.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml

# Check deployment status
kubectl get all -n ai-news-analyzer

# Get service URLs
kubectl get svc -n ai-news-analyzer
```

### Method 2: Using Terraform (Automated)

See [Terraform Automation](#terraform-automation) section below.

### Architecture

```
┌─────────────┐
│   Frontend  │ (LoadBalancer)
│  Port: 80   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Backend   │ (LoadBalancer)
│  Port: 8000 │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   MongoDB   │ (ClusterIP)
│  Port: 27017│
└─────────────┘
```

---

## Terraform Automation

### Initialize Terraform

```bash
cd terraform
terraform init
```

### Plan Deployment

```bash
terraform plan
```

### Deploy Infrastructure

```bash
terraform apply
```

Type `yes` when prompted, or use `-auto-approve` for non-interactive deployment:

```bash
terraform apply -auto-approve
```

### View Outputs

```bash
terraform output
```

### Customize Deployment

Edit `terraform/variables.tf` or create `terraform/terraform.tfvars`:

```hcl
namespace          = "ai-news-analyzer"
backend_replicas   = 3
frontend_replicas  = 3
mongodb_storage    = "5Gi"
```

Then apply:

```bash
terraform apply -var-file="terraform.tfvars"
```

### Destroy Infrastructure

```bash
cd terraform
terraform destroy
```

---

## Monitoring & Management

### Check Pod Status

```bash
kubectl get pods -n ai-news-analyzer
```

Expected output:
```
NAME                        READY   STATUS    RESTARTS   AGE
backend-xxxxxxxxx-xxxxx     1/1     Running   0          5m
backend-xxxxxxxxx-xxxxx     1/1     Running   0          5m
frontend-xxxxxxxxx-xxxxx    1/1     Running   0          5m
frontend-xxxxxxxxx-xxxxx    1/1     Running   0          5m
mongodb-xxxxxxxxx-xxxxx     1/1     Running   0          5m
```

### View Logs

```bash
# Backend logs
kubectl logs -n ai-news-analyzer -l app=backend --tail=100

# Frontend logs
kubectl logs -n ai-news-analyzer -l app=frontend --tail=100

# MongoDB logs
kubectl logs -n ai-news-analyzer -l app=mongodb --tail=100

# Follow logs in real-time
kubectl logs -n ai-news-analyzer -l app=backend -f
```

### Access Services

#### Get Service URLs

```bash
kubectl get svc -n ai-news-analyzer
```

#### Port Forwarding (for testing)

```bash
# Frontend
kubectl port-forward -n ai-news-analyzer svc/frontend 3000:80

# Backend
kubectl port-forward -n ai-news-analyzer svc/backend 8000:8000

# MongoDB (from within cluster only)
kubectl port-forward -n ai-news-analyzer svc/mongodb 27017:27017
```

### Scale Deployments

```bash
# Scale backend
kubectl scale deployment backend -n ai-news-analyzer --replicas=3

# Scale frontend
kubectl scale deployment frontend -n ai-news-analyzer --replicas=3
```

### Update Images

```bash
# Build new images
docker build -t mortadhajemai/ai-news-backend:v2 ./backend
docker push mortadhajemai/ai-news-backend:v2

# Update deployment
kubectl set image deployment/backend -n ai-news-analyzer \
  backend=mortadhajemai/ai-news-backend:v2

# Check rollout status
kubectl rollout status deployment/backend -n ai-news-analyzer
```

### Rollback Deployment

```bash
# Rollback to previous version
kubectl rollout undo deployment/backend -n ai-news-analyzer

# Rollback to specific revision
kubectl rollout undo deployment/backend -n ai-news-analyzer --to-revision=2

# View rollout history
kubectl rollout history deployment/backend -n ai-news-analyzer
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Describe pod to see events
kubectl describe pod <pod-name> -n ai-news-analyzer

# Check pod logs
kubectl logs <pod-name> -n ai-news-analyzer

# Check events
kubectl get events -n ai-news-analyzer --sort-by='.lastTimestamp'
```

### Common Issues

#### 1. ImagePullBackOff

**Problem**: Cannot pull Docker image

**Solution**:
```bash
# Verify image exists
docker pull mortadhajemai/ai-news-backend:latest

# Check image name in deployment
kubectl get deployment backend -n ai-news-analyzer -o yaml | grep image:
```

#### 2. CrashLoopBackOff

**Problem**: Pod keeps restarting

**Solution**:
```bash
# Check logs for errors
kubectl logs <pod-name> -n ai-news-analyzer --previous

# Check resource limits
kubectl describe pod <pod-name> -n ai-news-analyzer
```

#### 3. MongoDB Connection Failed

**Problem**: Backend cannot connect to MongoDB

**Solution**:
```bash
# Verify MongoDB is running
kubectl get pods -n ai-news-analyzer -l app=mongodb

# Check MongoDB service
kubectl get svc mongodb -n ai-news-analyzer

# Test connection from backend pod
kubectl exec -it <backend-pod> -n ai-news-analyzer -- \
  curl http://mongodb:27017
```

#### 4. LoadBalancer Pending

**Problem**: Service External-IP shows `<pending>`

**Solution**:

For **Minikube**:
```bash
minikube tunnel
```

For **Kind**:
```bash
# Use port-forward instead
kubectl port-forward -n ai-news-analyzer svc/frontend 3000:80
```

For **Cloud Providers**: LoadBalancer should be provisioned automatically.

#### 5. Terraform State Lock

**Problem**: Terraform state is locked

**Solution**:
```bash
cd terraform
terraform force-unlock <lock-id>
```

### Performance Issues

#### Check Resource Usage

```bash
# CPU and memory usage
kubectl top pods -n ai-news-analyzer

# Resource limits
kubectl describe pod <pod-name> -n ai-news-analyzer | grep -A 5 Resources
```

#### Increase Resources

Edit `k8s/backend.yaml` or `terraform/main.tf`:

```yaml
resources:
  limits:
    memory: "4Gi"
    cpu: "2000m"
  requests:
    memory: "2Gi"
    cpu: "1000m"
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│                   Internet                       │
└───────────────────┬─────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐    ┌────────▼────────┐
│   Frontend LB  │    │   Backend LB    │
│   External IP  │    │   External IP   │
└───────┬────────┘    └────────┬────────┘
        │                      │
┌───────▼────────┐    ┌────────▼────────┐
│  Frontend Pods │    │  Backend Pods   │
│  (2 replicas)  │    │  (2 replicas)   │
└────────────────┘    └────────┬────────┘
                               │
                      ┌────────▼────────┐
                      │  MongoDB (PVC)  │
                      │   ClusterIP     │
                      └─────────────────┘
```

---

## Configuration Files

### Directory Structure

```
AI-News-Analyzer/
├── k8s/
│   ├── namespace.yaml      # Namespace definition
│   ├── mongodb.yaml        # MongoDB deployment + PVC + service
│   ├── backend.yaml        # Backend deployment + ConfigMap + service
│   └── frontend.yaml       # Frontend deployment + service
├── terraform/
│   ├── main.tf            # Main Terraform configuration
│   ├── variables.tf       # Input variables
│   ├── outputs.tf         # Output values
│   └── providers.tf       # Provider configuration
├── scripts/
│   └── deploy.sh          # Automated deployment script
├── backend/
│   ├── Dockerfile         # Backend Docker image
│   └── .dockerignore
├── frontend/
│   ├── Dockerfile         # Frontend Docker image
│   ├── nginx.conf         # Nginx configuration
│   └── .dockerignore
└── DEVOPS.md             # This file
```

---

## Next Steps

1. **Set up CI/CD Pipeline**
   - GitHub Actions for automated builds
   - ArgoCD for GitOps deployment

2. **Add Monitoring**
   - Prometheus for metrics
   - Grafana for visualization
   - ELK Stack for logging

3. **Implement Security**
   - Network policies
   - Pod security policies
   - Secrets management (Vault)

4. **Enable Auto-scaling**
   - Horizontal Pod Autoscaler (HPA)
   - Vertical Pod Autoscaler (VPA)
   - Cluster Autoscaler

5. **Add Ingress Controller**
   - Nginx Ingress
   - Cert-manager for TLS
   - Custom domains

---

## Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- View Kubernetes logs
- Review Terraform state

**Happy Deploying! 🚀**
