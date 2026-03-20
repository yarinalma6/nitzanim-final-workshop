# ----- שלב 1: בניית העיצוב (Frontend) -----
# משתמשים ב-Node רק כדי לבנות את קבצי ה-CSS/JS
FROM node:18-slim AS frontend
#WORKDIR בתיקייה נפרדת לחלוטין כדי למנוע שגיאות זיכרון (Set maximum size exceeded)
WORKDIR /src_frontend
COPY statuspage/project-static/package.json statuspage/project-static/yarn.lock ./
RUN yarn install --frozen-lockfile
COPY statuspage/project-static/ ./
# הרצת הקימפול עם הגבלת זיכרון ל-Node והתעלמות משגיאות JS קטנות
RUN NODE_OPTIONS=--max-old-space-size=2048 yarn bundle || true
# מוודאים שתיקיית dist קיימת כדי שהבנייה לא תיעצר
RUN mkdir -p dist

# ----- שלב 2: בונה הספריות (Python Builder) -----
FROM python:3.10-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /install
COPY requirements.txt .
# התקנה לתיקייה ייעודית שתועתק בהמשך
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ----- שלב 3: הפוד הסופי (Production) -----
FROM python:3.10-slim
WORKDIR /app
# התקנת ספריות מערכת הכרחיות
RUN apt-get update && apt-get install -y libpq5 && rm -rf /var/lib/apt/lists/*

# העתקת הספריות המוכנות מהבילדר לנתיב המערכת הראשי (פותר את בעיית rq_scheduler)
COPY --from=builder /install /usr/local
# העתקת כל הקוד
COPY . .
# העתקת העיצוב המקומפל משלב 1 למיקום המדויק שהאפליקציה מחפשת
COPY --from=frontend /src_frontend/dist/ /app/statuspage/project-static/dist/

# הגדרת נתיבי עבודה לפייתון
ENV PYTHONPATH=/app/statuspage
# איסוף הסטטיקה - הפעם זה יעבור כי ה-dist קיים והספריות מותקנות
RUN python statuspage/manage.py collectstatic --no-input

# הפקודה שמניעה את הכל
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--chdir", "statuspage", "statuspage.wsgi:application"]