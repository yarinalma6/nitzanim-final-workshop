# ----- שלב 1: קימפול עיצוב (Frontend) -----
FROM node:18-slim AS frontend
WORKDIR /build
# העתקה של קבצי הסטטיקה בלבד כדי ש-Node לא יתברבר בסריקת קבצים מיותרים
COPY statuspage/project-static/package.json statuspage/project-static/yarn.lock ./
RUN yarn install --frozen-lockfile
COPY statuspage/project-static/ .
# הרצת הקימפול. הוספנו הגבלת זיכרון ל-Node
RUN NODE_OPTIONS=--max-old-space-size=2048 yarn bundle || true

# ----- שלב 2: בונה הספריות (Python Builder) -----
FROM python:3.10-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /install
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ----- שלב 3: הפוד הסופי (Production) -----
FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libpq5 && rm -rf /var/lib/apt/lists/*

# העתקת הספריות המוכנות
COPY --from=builder /install /usr/local
# העתקת הקוד
COPY . .
# העתקת העיצוב המקומפל למיקום המדויק שהאפליקציה מחפשת
COPY --from=frontend /build/dist/ /app/statuspage/project-static/dist/

# הגדרת נתיבים
ENV PYTHONPATH=/app/statuspage
# איסוף סטטיקה
RUN python statuspage/manage.py collectstatic --no-input

# הרצה
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--chdir", "statuspage", "statuspage.wsgi:application"]