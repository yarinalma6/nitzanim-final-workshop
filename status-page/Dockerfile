# ----- שלב 1: בניית העיצוב (Frontend) באמצעות Node.js -----
# משתמשים בתמונה של Node כבסיס כדי לקמפל את העיצוב
FROM node:18 AS frontend
# הגדרת תיקיית עבודה
WORKDIR /app
# העתקת קבצי ניהול החבילות של העיצוב והתקנתן
COPY statuspage/project-static/package.json statuspage/project-static/yarn.lock ./
RUN yarn install
# העתקת שאר קבצי העיצוב (SCSS/TS) וקימפול שלהם ל-CSS תקין
COPY statuspage/project-static/ ./
RUN yarn bundle


# ----- שלב 2: סביבת הפייתון והתקנת ספריות (Builder) -----
# משתמשים בתמונה של פייתון כבסיס
FROM python:3.10-slim AS builder
# הגדרת משתני סביבה כדי שפייתון לא ייצור קבצי .pyc מיותרים
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# התקנת תלויות של מערכת ההפעלה (אם צריך קומפיילרים)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# הגדרת תיקיית עבודה
WORKDIR /app
# העתקת קובץ הדרישות והתקנת הספריות
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# ----- שלב 3: הפוד הסופי (Production) -----
FROM python:3.10-slim
WORKDIR /app
# הוספנו את השורות האלו - התקנת הספריה שחסרה להרצה ב-Postgres
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*
# מעתיקים את הספריות מהבילדר
COPY --from=builder /root/.local /root/.local
# מעדכנים את ה-PATH כדי שהמערכת תכיר את gunicorn
ENV PATH=/root/.local/bin:$PATH
# מעתיקים את הקוד (ה-dockerignore כבר דואג שזה יהיה נקי)
COPY . .
# פה הקסם: מעתיקים את העיצוב המוכן משלב 1, ישר לתיקייה שפייתון מחפש!
COPY --from=frontend /app/dist/ /app/statuspage/project-static/dist/
# הרצת איסוף קבצי הסטטיקה כבר בשלב בניית האימג' כדי שהעיצוב יהיה מוכן מראש
RUN python statuspage/manage.py collectstatic --no-input
# הפקודה שמניעה את הכל
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "statuspage.wsgi:application"]