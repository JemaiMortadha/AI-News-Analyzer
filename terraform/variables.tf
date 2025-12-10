variable "namespace" {
  description = "Kubernetes namespace for the application"
  type        = string
  default     = "ai-news-analyzer"
}

variable "dockerhub_username" {
  description = "DockerHub username"
  type        = string
  default     = "mortadhajemai"
}

variable "backend_replicas" {
  description = "Number of backend replicas"
  type        = number
  default     = 2
}

variable "frontend_replicas" {
  description = "Number of frontend replicas"
  type        = number
  default     = 2
}

variable "mongodb_storage" {
  description = "Storage size for MongoDB PVC"
  type        = string
  default     = "1Gi"
}
