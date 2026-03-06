module "ecr" {
  source = "terraform-aws-modules/ecr/aws"

  repository_name = "yarin-noa-project"

  repository_read_write_access_arns = ["arn:aws:iam::992382545251:role/GithubAction-ECR-Role-yarin"]
  repository_lifecycle_policy = jsonencode({
    rules = [
      {
        rulePriority = 1,
        description  = "Keep last 30 images",
        selection = {
          tagStatus     = "any",
          countType     = "imageCountMoreThan",
          countNumber   = 30
        },
        action = {
          type = "expire"
        }
      }
    ]
  })

  tags = {
    Project = "StatusPage"
    Terraform   = "True"
    Owner = "Yarin"
  }
}