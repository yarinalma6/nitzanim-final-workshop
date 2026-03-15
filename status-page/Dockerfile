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


FROM python:3.10-slim
WORKDIR /app
# מעתיקים את הספריות מהבילדר
COPY --from=builder /root/.local /root/.local
# מעדכנים את ה-PATH כדי שהמערכת תכיר את gunicorn
ENV PATH=/root/.local/bin:$PATH
# מעתיקים את הקוד (ה-dockerignore כבר דואג שזה יהיה נקי)
COPY . .
# הפקודה שמניעה את הכל - שים לב לשינוי בשם החבילה
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "statuspage.wsgi:application"]