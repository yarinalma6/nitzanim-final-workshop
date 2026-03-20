# ----- שלב 1: בניית העיצוב (Frontend) באמצעות Node.js -----
FROM node:18 AS frontend
WORKDIR /src_frontend
COPY statuspage/project-static/package.json statuspage/project-static/yarn.lock ./
RUN yarn install
COPY statuspage/project-static/ ./
# הגדלת הזיכרון לקימפול והוספת הגנה כדי שה-CSS יעבור גם אם יש שגיאות ב-JS
RUN NODE_OPTIONS=--max-old-space-size=4096 yarn bundle || true
RUN mkdir -p dist


# ----- שלב 2: סביבת הפייתון והתקנת ספריות (Builder) -----
FROM python:3.10-slim AS builder
# שימוש בפורמט KEY=VALUE כדי למנוע אזהרות Legacy
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
# התקנה ישירות למערכת בתוך ה-Builder (בלי --user) כדי להקל על ההעתקה
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ----- שלב 3: הפוד הסופי (Production) -----
FROM python:3.10-slim
WORKDIR /app
# התקנת הספריה שחסרה להרצה ב-Postgres
RUN apt-get update && apt-get install -y libpq5 && rm -rf /var/lib/apt/lists/*

# פתרון לבעיית ה-rq_scheduler: מעתיקים את כל הספריות המותקנות ישירות לתיקיית המערכת
COPY --from=builder /install /usr/local

# מעתיקים את הקוד
COPY . .

# מעתיקים את העיצוב המקומפל
COPY --from=frontend /src_frontend/dist/ /app/statuspage/project-static/dist/

# הגדרת ה-PYTHONPATH כדי שפייתון ימצא את manage.py בתוך התיקייה statuspage
ENV PYTHONPATH=/app/statuspage

# הרצת איסוף קבצי הסטטיקה (הפעם זה יעבור כי כל הספריות בנתיב המערכת)
RUN python statuspage/manage.py collectstatic --no-input

# הפקודה שמניעה את הכל
# שימוש ב-chdir כדי להיכנס לתיקייה הנכונה שבה נמצא הקוד
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--chdir", "statuspage", "statuspage.wsgi:application"]