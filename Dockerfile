FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -m appuser

# Install gosu so the entrypoint can drop privileges cleanly
RUN apt-get update && apt-get install -y --no-install-recommends gosu && \
    rm -rf /var/lib/apt/lists/*


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
RUN chmod +x /app/entrypoint.sh
RUN chmod a+rw .
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "main.py"]