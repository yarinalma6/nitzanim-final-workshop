module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = "yarin-noa-cluster"
  kubernetes_version = "1.35"

# --- חלק חדש: תוספים קריטיים לרשת (פותר את הבעיה שהנודים לא עולים) ---
  addons = {
    # תוסף הרשת שנותן כתובות IP לפודים
    vpc-cni    = {
      most_recent    = true
      before_compute = true  # מתקין את הרשת לפני השרתים
    }
    # שירות השמות הפנימי של הקלאסטר
    coredns    = {
      most_recent = true
    }
    # אחראי על ניתוב התקשורת בתוך הקלאסטר
    kube-proxy = {
      most_recent = true
    }
  }
  # -----------------------

  # Optional
  endpoint_public_access = true

  # Optional: Adds the current caller identity as an administrator via cluster access entry
  enable_cluster_creator_admin_permissions = true

  # הגדרת השרתים שיריצו את האפליקציות שלכם
  eks_managed_node_groups = {
    general = {
      instance_types = ["t3.medium"] # סוג מכונה יחסית זול אבל מספיק חזק
      min_size     = 1
      max_size     = 3
      desired_size = 2 # כמה שרתים ירוצו ביום-יום
    }
  }

  vpc_id = module.vpc.vpc_id

  subnet_ids = module.vpc.private_subnets

  enable_irsa = true

  tags = {
    Owner     = "Yarin"
    Terraform = "true"
    Project   = "StatusPage"
  }
}