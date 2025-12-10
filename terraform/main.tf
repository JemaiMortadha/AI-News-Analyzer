# Create namespace
resource "kubernetes_namespace" "ai_news" {
  metadata {
    name = var.namespace
    labels = {
      app = "ai-news-analyzer"
    }
  }
}

# MongoDB PVC
resource "kubernetes_persistent_volume_claim" "mongodb" {
  metadata {
    name      = "mongodb-pvc"
    namespace = kubernetes_namespace.ai_news.metadata[0].name
  }
  spec {
    access_modes = ["ReadWriteOnce"]
    resources {
      requests = {
        storage = var.mongodb_storage
      }
    }
  }
}

# MongoDB Deployment
resource "kubernetes_deployment" "mongodb" {
  metadata {
    name      = "mongodb"
    namespace = kubernetes_namespace.ai_news.metadata[0].name
  }
  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "mongodb"
      }
    }
    template {
      metadata {
        labels = {
          app = "mongodb"
        }
      }
      spec {
        container {
          name  = "mongodb"
          image = "mongo:7.0"
          port {
            container_port = 27017
          }
          volume_mount {
            name       = "mongodb-storage"
            mount_path = "/data/db"
          }
          resources {
            limits = {
              memory = "512Mi"
              cpu    = "500m"
            }
          }
        }
        volume {
          name = "mongodb-storage"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.mongodb.metadata[0].name
          }
        }
      }
    }
  }
}

# MongoDB Service
resource "kubernetes_service" "mongodb" {
  metadata {
    name      = "mongodb"
    namespace = kubernetes_namespace.ai_news.metadata[0].name
  }
  spec {
    selector = {
      app = "mongodb"
    }
    port {
      port        = 27017
      target_port = 27017
    }
    type = "ClusterIP"
  }
}

# Backend ConfigMap
resource "kubernetes_config_map" "backend" {
  metadata {
    name      = "backend-config"
    namespace = kubernetes_namespace.ai_news.metadata[0].name
  }
  data = {
    MONGODB_HOST = "mongodb"
    MONGODB_PORT = "27017"
    MONGODB_NAME = "ai_news_analyzer"
  }
}

# Backend Deployment
resource "kubernetes_deployment" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace.ai_news.metadata[0].name
  }
  spec {
    replicas = var.backend_replicas
    selector {
      match_labels = {
        app = "backend"
      }
    }
    template {
      metadata {
        labels = {
          app = "backend"
        }
      }
      spec {
        container {
          name  = "backend"
          image = "${var.dockerhub_username}/ai-news-backend:latest"
          port {
            container_port = 8000
          }
          env_from {
            config_map_ref {
              name = kubernetes_config_map.backend.metadata[0].name
            }
          }
          resources {
            limits = {
              memory = "2Gi"
              cpu    = "1000m"
            }
            requests = {
              memory = "1Gi"
              cpu    = "500m"
            }
          }
          liveness_probe {
            http_get {
              path = "/api/articles/"
              port = 8000
            }
            initial_delay_seconds = 30
            period_seconds        = 10
          }
          readiness_probe {
            http_get {
              path = "/api/articles/"
              port = 8000
            }
            initial_delay_seconds = 20
            period_seconds        = 5
          }
        }
      }
    }
  }
  depends_on = [kubernetes_deployment.mongodb]
}

# Backend Service
resource "kubernetes_service" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace.ai_news.metadata[0].name
  }
  spec {
    selector = {
      app = "backend"
    }
    port {
      port        = 8000
      target_port = 8000
    }
    type = "LoadBalancer"
  }
}

# Frontend Deployment
resource "kubernetes_deployment" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace.ai_news.metadata[0].name
  }
  spec {
    replicas = var.frontend_replicas
    selector {
      match_labels = {
        app = "frontend"
      }
    }
    template {
      metadata {
        labels = {
          app = "frontend"
        }
      }
      spec {
        container {
          name  = "frontend"
          image = "${var.dockerhub_username}/ai-news-frontend:latest"
          port {
            container_port = 80
          }
          resources {
            limits = {
              memory = "256Mi"
              cpu    = "200m"
            }
            requests = {
              memory = "128Mi"
              cpu    = "100m"
            }
          }
          liveness_probe {
            http_get {
              path = "/"
              port = 80
            }
            initial_delay_seconds = 10
            period_seconds        = 10
          }
          readiness_probe {
            http_get {
              path = "/"
              port = 80
            }
            initial_delay_seconds = 5
            period_seconds        = 5
          }
        }
      }
    }
  }
  depends_on = [kubernetes_deployment.backend]
}

# Frontend Service
resource "kubernetes_service" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace.ai_news.metadata[0].name
  }
  spec {
    selector = {
      app = "frontend"
    }
    port {
      port        = 80
      target_port = 80
    }
    type = "LoadBalancer"
  }
}
