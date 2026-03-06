################################################################################
# VPC Outputs
################################################################################
output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

################################################################################
# EKS Outputs
################################################################################
output "eks_cluster_name" {
  description = "The name of the EKS cluster"
  value       = module.eks.cluster_name
}

################################################################################
# ECR Outputs
################################################################################
output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = module.ecr.repository_url
}

################################################################################
# Secrets Manager Outputs
################################################################################
output "app_secrets_arn" {
  description = "The ARN of the App Secrets"
  value       = aws_secretsmanager_secret.app_secrets.arn
}