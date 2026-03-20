# משתמשים בתמונה של פייתון כבסיס
FROM python:3.10-slim

# הגדרת משתני סביבה בפורמט תקין
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/statuspage

# התקנת תלויות מערכת הפעלה (כולל אלו שצריך ל-psycopg2 ואיסוף סטטיקה)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# הגדרת תיקיית עבודה
WORKDIR /app

# העתקת דרישות והתקנה גלובלית (מונע שגיאות של rq_scheduler)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# העתקת כל הקוד
COPY . .

# הרצת איסוף הסטטיקה בזמן הבנייה - הנתיב תוקן לפי המבנה שלך
RUN python statuspage/manage.py collectstatic --no-input

# פקודת ההרצה שתמיד עבדה (עם chdir לתיקייה הנכונה)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--chdir", "statuspage", "statuspage.wsgi:application"]