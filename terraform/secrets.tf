################################################################################
# Secrets Manager - "הכספת" (The Safe)
################################################################################

resource "aws_secretsmanager_secret" "app_secrets" {
  # השם הקבוע שנחפש אחר כך בקוברנטיס
  name                    = "statuspage-yarin-noa-secrets"

  # מאפשר למחוק וליצור מחדש מיד בלי לחכות שבוע (מומלץ לפיתוח)
  recovery_window_in_days = 0

  tags = {
    Terraform = "true"
    Owner     = "Yarin"
    Project   = "StatusPage"
  }
}

################################################################################
# Secret Version - "התוכן של הכספת" (The Content)
################################################################################

resource "aws_secretsmanager_secret_version" "app_secrets_version" {
  secret_id     = aws_secretsmanager_secret.app_secrets.id

  # ערכי פלסבו ראשוניים - ישונו ידנית בקונסול של AWS
  secret_string = jsonencode({
    SECRET_KEY = "placeholder-to-be-changed-manually"
    DEBUG      = "True"
  })

  # החלק הקריטי: אומר לטרהפורם "תיצור פעם אחת, ואז אל תסתכל יותר על התוכן"
  lifecycle {
    ignore_changes = [
      secret_string,
    ]
  }
}