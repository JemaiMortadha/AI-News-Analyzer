output "frontend_url" {
  description = "Frontend service URL"
  value       = "Pending LoadBalancer assignment - run 'kubectl get svc -n ${var.namespace} frontend'"
}

output "backend_url" {
  description = "Backend API URL"
  value       = "Pending LoadBalancer assignment - run 'kubectl get svc -n ${var.namespace} backend'"
}

output "mongodb_service" {
  description = "MongoDB service endpoint"
  value       = "mongodb.${var.namespace}.svc.cluster.local:27017"
}

output "deployment_status" {
  description = "How to check deployment status"
  value       = "kubectl get all -n ${var.namespace}"
}
