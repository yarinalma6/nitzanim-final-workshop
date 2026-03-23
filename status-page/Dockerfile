# --- שלב 1: קימפול העיצוב (Node.js) ---
FROM node:18-slim AS frontend
WORKDIR /frontend

# העתקת כל הפרויקט כדי ש-Tailwind יוכל לסרוק את קבצי ה-HTML וה-Python
COPY . .

WORKDIR /frontend/statuspage/project-static
RUN yarn install
RUN yarn bundle || true

# --- שלב 2: פייתון (Production) ---
FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# התקנת תלויות מערכת
RUN apt-get update && apt-get install -y build-essential libpq-dev libpq5 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
# התקנת כל הדרישות + rq-scheduler מראש כדי שלא יהיו שגיאות
RUN pip install --no-cache-dir -r requirements.txt rq-scheduler

# העתקת כל הקוד
COPY . .
# העתקת העיצוב המוכן משלב 1 ישר לתיקייה הנכונה
COPY --from=frontend /frontend/statuspage/project-static/dist/ /app/statuspage/project-static/dist/

# איסוף קבצים סטטיים ל-WhiteNoise
RUN python statuspage/manage.py collectstatic --noinput

# הפקודה שמניעה את הכל
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--chdir", "statuspage", "statuspage.wsgi:application"]