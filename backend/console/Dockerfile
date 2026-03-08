
# Use a slim Python 3.11 base image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools wheel \
	&& pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app/backend
COPY gen/py /app/gen/py


ENV PYTHONPATH="/app/gen/py/src:/app"

# Expose the typical HTTP port; adjust if your app uses a different one
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "openapi_server.main:app", "--host", "0.0.0.0", "--port", "8000"]

