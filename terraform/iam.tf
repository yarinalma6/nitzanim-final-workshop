resource "aws_iam_role" "lb_controller" {
  name = "status-page-lb-controller-role-manual"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRoleWithWebIdentity"
      Effect = "Allow"
      Principal = {
        Federated = "arn:aws:iam::992382545251:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/F29FCAB7C305C8D839E7DB754D51F5D3"
      }
      Condition = {
        StringEquals = {
          "oidc.eks.us-east-1.amazonaws.com/id/F29FCAB7C305C8D839E7DB754D51F5D3:aud" = "sts.amazonaws.com"
          "oidc.eks.us-east-1.amazonaws.com/id/F29FCAB7C305C8D839E7DB754D51F5D3:sub" = "system:serviceaccount:kube-system:aws-load-balancer-controller"
        }
      }
    }]
  })
  managed_policy_arns = ["arn:aws:iam::992382545251:policy/AWSLoadBalancerControllerIAMPolicy"]
}

resource "aws_iam_role" "external_dns" {
  name = "status-page-external-dns-role-fixed"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRoleWithWebIdentity"
      Effect = "Allow"
      Principal = {
        Federated = "arn:aws:iam::992382545251:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/F29FCAB7C305C8D839E7DB754D51F5D3"
      }
      Condition = {
        StringEquals = {
          "oidc.eks.us-east-1.amazonaws.com/id/F29FCAB7C305C8D839E7DB754D51F5D3:aud" = "sts.amazonaws.com"
          "oidc.eks.us-east-1.amazonaws.com/id/F29FCAB7C305C8D839E7DB754D51F5D3:sub" = "system:serviceaccount:kube-system:external-dns"
        }
      }
    }]
  })
  managed_policy_arns = ["arn:aws:iam::992382545251:policy/ExternalDNSPolicy-AA"]
}