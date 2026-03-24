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

RUN apt-get update && apt-get install -y build-essential libpq-dev libpq5 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir rq==1.11.1 rq-scheduler==0.11.0

# העתקת כל הקבצים (כולל מה שנוצר בשלב ה-Frontend)
COPY --from=frontend /app /app

# --- התיקון הקריטי: מעבר לתיקייה הנכונה והוספת משתני סביבה ---
WORKDIR /app/statuspage

# הורדנו את ה- || true ותיקנו ל- --noinput. משתני הסביבה מונעים קריסה של ג'אנגו.
RUN SECRET_KEY="dummy" DB_HOST="localhost" POSTGRES_PASSWORD="dummy" REDIS_HOST="localhost" python manage.py collectstatic --noinput
# הפעלת Gunicorn (אין צורך ב-chdir כי אנחנו כבר בתיקייה הנכונה)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "statuspage.wsgi:application"]