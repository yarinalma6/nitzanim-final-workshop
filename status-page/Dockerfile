# --- שלב 1: קימפול הפרונטאנד (Node.js) ---
FROM node:18-slim AS frontend
WORKDIR /app
COPY . .
WORKDIR /app/statuspage/project-static
RUN yarn install
RUN yarn bundle

# --- שלב 2: סביבת הפרודקשן (Python) ---
FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# התקנת media-types (התחליף ל-mime-support) קריטית להגשת CSS תקין ב-WhiteNoise
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libpq5 \
    media-types \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir rq==1.11.1 rq-scheduler==0.11.0

# העתקת הקבצים מה-Frontend Build
COPY --from=frontend /app /app

WORKDIR /app/statuspage

# יצירת התיקייה והרצת collectstatic בשלב ה-Build
RUN mkdir -p /app/statuspage/static
RUN SECRET_KEY="dummy" \
    ALLOWED_HOSTS="*" \
    DATABASE_NAME="dummy" \
    REDIS_HOST="localhost" \
    SITE_URL="https://status.yarin-noa.site" \
    python manage.py collectstatic --noinput

# הפעלת Gunicorn על פורט 8000 כפי שמוגדר ב-Deployment
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "statuspage.wsgi:application"]