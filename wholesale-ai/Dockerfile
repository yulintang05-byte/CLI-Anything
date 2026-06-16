FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Data directory for pipeline + profile persistence
VOLUME ["/root/.wholesale-ai"]

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "main.py"]
