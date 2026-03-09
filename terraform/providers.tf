# הגדרת הבלוק הראשי של טרהפורם והגרסאות הנדרשות
terraform {
  # רשימת התוספים (Providers) שטרהפורם חייב להוריד כדי לעבוד
  required_providers {

    # הפרוביידר של AWS - אחראי על יצירת משאבי הענן (VPC, EKS, ECR)
    aws = {
      source  = "hashicorp/aws" # המקור ממנו מורידים את הפלאגין
      version = "~> 6.0"        # דרישה לגרסה 6 ומעלה כדי שיתמוך במודולים החדשים
    }

    # הפרוביידר של Helm - אחראי על התקנת חבילות תוכנה בתוך הקלאסטר (כמו ArgoCD)
    helm = {
      source  = "hashicorp/helm" # המקור של הפלאגין
      version = "~> 2.12"        # גרסה יציבה לעבודה מול קוברנטיס
    }
  }
}

# הגדרת חיבור הבסיס ל-AWS
provider "aws" {
  region = "us-east-1" # האזור (Region) שבו יוקמו כל המשאבים
}

# הגדרת אופן החיבור של Helm לקלאסטר הקוברנטיס שלנו
provider "helm" {
  kubernetes {
    # הכתובת של ה-API של הקלאסטר (נלקחת אוטומטית מהפלט של יצירת ה-EKS)
    host                   = module.eks.cluster_endpoint

    # תעודת האבטחה של הקלאסטר (מקודדת ב-Base64, לכן אנחנו מפענחים אותה)
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

    # מנגנון יצירת טוקן זמני - טרהפורם משתמש ב-AWS CLI שמותקן אצלך כדי להזדהות מול הקלאסטר
    exec {
      api_version = "client.authentication.k8s.io/v1beta1" # גרסת ה-API של ההזדהות
      args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name] # הפקודה שמייצרת את הטוקן
      command     = "aws" # הכלי שיריץ את הפקודה (AWS CLI)
    }
  }
}