# שימוש במשאב של Helm כדי להתקין חבילה (Release) חדשה בקלאסטר
resource "helm_release" "argocd" {
  name             = "argocd"                                 # השם שניתן להתקנה בתוך הקלאסטר
  repository       = "https://argoproj.github.io/argo-helm"   # הכתובת האינטרנטית של החנות הרשמית של ArgoCD
  chart            = "argo-cd"                                # שם החבילה (Chart) שאנחנו רוצים להתקין מהחנות
  namespace        = "argocd"                                 # "החדר" (Namespace) בתוך קוברנטיס שבו יוקמו הפודים של ArgoCD
  create_namespace = true                                     # אומר להלם: "אם החדר argocd לא קיים, תיצור אותו בעצמך"
  version          = "5.51.6"                                 # גרסת ה-Chart היציבה שאנחנו מתקינים (Best Practice לאבטחה)

  # בלוק תלות (Dependency) - החלק הקריטי ביותר בקובץ!
  # אומר לטרהפורם: "אסור לך לנסות להתקין את ArgoCD לפני שמודול ה-EKS (הקלאסטר כולל השרתים) סיים להיווצר בהצלחה"
  depends_on = [
    module.eks
  ]
}