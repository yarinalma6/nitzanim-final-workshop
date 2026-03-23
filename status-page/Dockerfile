# --- שלב 1: קימפול הפרונטאנד (Node.js) ---
FROM node:18-slim AS frontend
WORKDIR /app
COPY . .
WORKDIR /app/statuspage/project-static
RUN yarn install
RUN yarn bundle || true

# --- שלב 2: סביבת הפרודקשן (Python) ---
FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential libpq-dev libpq5 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# הפתרון המקצועי: קיבוע גרסאות שעובדות בהרמוניה כדי למנוע ImportError
RUN pip install --no-cache-dir rq==1.11.1 rq-scheduler==0.11.0

COPY --from=frontend /app /app
RUN python manage.py collectstatic --no-input || true

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--chdir", "statuspage", "statuspage.wsgi:application"]