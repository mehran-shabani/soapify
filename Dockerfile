FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=voice_summarizer.settings \
    PORT=8000

WORKDIR /app

RUN addgroup --system app \
    && adduser --system --ingroup app app

COPY --chown=app:app voice_summarizer/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app . .

USER app

EXPOSE 8000

CMD ["/bin/sh", "-c", "exec gunicorn --bind 0.0.0.0:$PORT voice_summarizer.wsgi:application"]
