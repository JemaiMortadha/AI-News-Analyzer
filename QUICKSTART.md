# 🚀 Quick Reference - DevOps Deployment

## Docker Images on DockerHub

✅ **Backend**: `mortadhajemai/ai-news-backend:latest`
✅ **Frontend**: `mortadhajemai/ai-news-frontend:latest`

## Deployment Commands

### Full Automated Deployment
```bash
./scripts/deploy.sh
```

### Manual Kubernetes Deployment
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/mongodb.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
```

### Terraform Deployment
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Check Status
```bash
kubectl get all -n ai-news-analyzer
kubectl get svc -n ai-news-analyzer
kubectl logs -n ai-news-analyzer -l app=backend
```

## Access Services
```bash
# Get external IPs
kubectl get svc -n ai-news-analyzer

# Port forward for local testing
kubectl port-forward -n ai-news-analyzer svc/frontend 3000:80
kubectl port-forward -n ai-news-analyzer svc/backend 8000:8000
```

## Scale Deployment
```bash
kubectl scale deployment backend -n ai-news-analyzer --replicas=3
kubectl scale deployment frontend -n ai-news-analyzer --replicas=3
```

## Cleanup
```bash
# Using Terraform
cd terraform && terraform destroy

# Using kubectl
kubectl delete namespace ai-news-analyzer
```

## Documentation
- **Complete Guide**: `DEVOPS.md`
- **Walkthrough**: `.gemini/antigravity/brain/.../walkthrough.md`
- **Original README**: `README.md`
