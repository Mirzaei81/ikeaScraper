FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd -ms /bin/bash admin

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=admin:admin . /app
RUN chmod +x /app/entrypoint.sh
RUN chmod 775 /app

USER admin
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "main.py"]