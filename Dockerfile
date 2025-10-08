FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=voice_summarizer.settings \
    PORT=8000

WORKDIR /app

COPY voice_summarizer/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "voice_summarizer/manage.py", "runserver", "0.0.0.0:8000"]
