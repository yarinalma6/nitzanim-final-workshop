# 🟢 Nitzanim DevOps Workshop - Final Project

## 🏗️ Project Overview
This repository contains the complete infrastructure and application lifecycle for the **StatusPage** project, developed as part of the Nitzanim DevOps Bootcamp final workshop. The project demonstrates a production-ready DevOps pipeline, from Infrastructure as Code (IaC) to GitOps-based deployment and comprehensive observability.

**Developed by**: Yarin & Noa 🚀

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Cloud Provider** | AWS (VPC, EKS, ECR, Route53, ACM) |
| **IaC** | Terraform |
| **Orchestration** | Kubernetes (EKS v1.35) |
| **GitOps** | ArgoCD |
| **CI/CD** | GitHub Actions |
| **Observability** | Prometheus, Grafana, Loki |
| **Secrets** | External Secrets Operator (ESO) |
| **Networking** | AWS ALB Ingress Controller, External-DNS |

---

## 📐 Architecture

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '18px', 'fontFamily': 'Inter, system-ui, sans-serif'}}}%%
graph TD
    %% Global Styles
    classDef aws fill:#FF9900,stroke:#232F3E,stroke-width:3px,color:white,font-weight:bold,padding:20px;
    classDef k8s fill:#326ce5,stroke:#fff,stroke-width:3px,color:white,font-weight:bold,padding:20px;
    classDef db fill:#333,stroke:#f80,stroke-width:3px,color:white,font-weight:bold,padding:20px;
    classDef gh fill:#24292e,stroke:#fff,stroke-width:3px,color:white,font-weight:bold,padding:20px;
    classDef app fill:#28a745,stroke:#fff,stroke-width:3px,color:white,font-weight:bold,padding:20px;

    subgraph "🌐 External Traffic"
        DNS["☁️ Route53: status.yarin-noa.site"]:::aws --> ALB["🔌 AWS Application Load Balancer"]:::aws
    end

    subgraph "⚙️ DevOps Infrastructure (Terraform)"
        TF["🚜 Terraform IaC"]:::gh -->|State| S3["📦 S3 Bucket: State Store"]:::aws
        TF -->|Provision| VPC["🌐 AWS VPC (Private/Public)"]:::aws
        TF -->|Provision| EKS["☸️ AWS EKS Cluster"]:::aws
    end

    subgraph "🐙 GitHub Ecosystem"
        Repo["📂 GitHub Repo (Single Source of Truth)"]:::gh --> GHA["🤖 GitHub Actions (CI/CD)"]:::gh
        GHA -->|1. Build & Push| ECR["📦 Amazon ECR Registry"]:::aws
    end

    subgraph "☸️ AWS EKS Cluster (v1.35)"
        ALB --> Ing["🕸️ ALB Ingress Controller"]:::k8s
        Ing --> SVC["🔌 K8s Service"]:::k8s
        
        subgraph "🚀 Application Layer"
            SVC --> Pods["📱 StatusPage Pods (Gunicorn)"]:::app
            Worker["👷 Background Worker (RQ)"]:::app
            Init["🏁 Init: Run Migrations"]:::app -.-> Pods
        end

        ECR -->|3. Pull Image| Pods
        ECR -->|3. Pull Image| Worker

        subgraph "💾 Persistence & Cache"
            Pods --> DB[("🐘 PostgreSQL DB")]:::db
            Worker --> DB
            Pods --> Cache[("🔋 Redis Cache")]:::db
            Worker --> Cache
        end
        
        Argo["🐙 ArgoCD (GitOps)"]:::k8s -- "2. Watch & Sync Manifests" --> Repo
        Argo -- "Update Deployment" --> Pods
        Argo -- "Update Deployment" --> Worker
        
        subgraph "🔐 Security"
            ESO["🔑 External Secrets Operator"]:::k8s -->|Fetch| SM["🔐 AWS Secrets Manager"]:::aws
            SM -->|Sync| K8sSec["📄 K8s Secret"]:::k8s
            K8sSec -.->|Inject| Pods
        end
        
        subgraph "📊 Observability"
            Prom["📈 Prometheus"]:::k8s -->|Scrape| Pods
            Graf["🎨 Grafana"]:::k8s -->|Visualize| Prom
            Loki["📝 Loki"]:::k8s -->|Logs| Pods
        end
    end
```

---

## 🚀 Deployment Pipeline

### 1. Infrastructure (IaC) - Terraform Depth
The foundational infrastructure is managed via **Terraform**, providing a repeatable and version-controlled environment.
- **Remote Backend**: Uses an **S3 Bucket** (`nitzanim-tf-state-yarin-noa`) for state storage, ensuring consistency and enabling collaboration.
- **VPC Module**: 
    - Configured across **2 Availability Zones** (us-east-1a, us-east-1b).
    - **Public Subnets**: Host the Load Balancer and NAT Gateway.
    - **Private Subnets**: Host the EKS Worker Nodes for enhanced security.
    - **NAT Gateway**: Allows private nodes to access the internet (e.g., for pulling updates) without being directly reachable from outside.
- **EKS Module**: 
    - **Version**: 1.35.
    - **Worker Nodes**: Managed Node Groups using `t3.medium` instances for a balance of cost and performance.
    - **OIDC Provider**: Enabled to support **IRSA** (IAM Roles for Service Accounts).
- **IAM & IRSA**: 
    - Fine-grained permissions for cluster add-ons.
    - Dedicated roles for the **AWS Load Balancer Controller** and **External-DNS**, allowing them to interact securely with AWS APIs (ALB, Route53) using Kubernetes ServiceAccounts.
- **ECR**: Private container registry with lifecycle policies to manage image versions.
- **ArgoCD Bootstrap**: Automatically deployed via Terraform's Helm provider once the cluster is ready.

### 2. CI/CD Flow
The application follows a standard CI/CD process:
1. **Developer Push**: Code changes are pushed to `main`.
2. **GH Actions**: Triggers a build-and-push workflow.
3. **Build**: Docker image is built using `BUILDKIT` for caching optimization.
4. **Push**: Image is pushed to **Amazon ECR** with the commit SHA and `latest` tags.
5. **Sync**: **ArgoCD** detects changes in the `/k8s` directory and automatically reconciles the cluster state.

### 3. Kubernetes Orchestration
Manifests are organized in the `/k8s` directory and managed by ArgoCD:
- **Deployments**: Django app and asynchronous workers.
- **Networking**: Ingress resources configured for AWS ALB with automated SSL/TLS termination via ACM.
- **ExternalDNS**: Automatically synchronizes ingress hosts with Route53.

---

## 📊 Observability & Monitoring
The cluster is equipped with a full monitoring stack installed via customized Helm charts:
- **Prometheus**: Metrics collection for cluster and application performance.
- **Grafana**: Pre-configured dashboards for easy visualization of system health.
- **Loki**: Centralized logging for real-time log exploration.
- **Access**: Easy access scripts available in `k8s/monitoring` and `k8s/logging`.

---

## 🔐 Security & Secrets
- **Secrets Management**: Sensitive data (DB credentials, API keys) are not stored in Git. Instead, they are managed by the **External Secrets Operator (ESO)**, which securely fetches them from **AWS Secrets Manager**.
- **Network Isolation**: Application nodes are located in private subnets, with only the Load Balancer exposed to the internet.

---

## 📂 Project Structure
```text
.
├── .github/workflows/   # CI/CD Workflows
├── k8s/                # Kubernetes Manifests (App, Monitoring, Logging)
├── status-page/        # Application Source Code & Dockerfile
├── terraform/          # Infrastructure as Code
└── eso.yaml            # External Secrets Configuration
```

---

## 📝 How to Use
1. **Initialize Infrastructure**:
   ```bash
   cd terraform
   terraform init
   terraform apply
   ```
2. **Access ArgoCD**:
   The `argocd.tf` script handles the installation. Access the UI to monitor the `status-page` application sync status.
3. **Monitoring**:
   Use the scripts in `k8s/monitoring/` to open Grafana and view pre-configured dashboards.

---
*Created for the Nitzanim Bootcamp Final Workshop - 2026*
