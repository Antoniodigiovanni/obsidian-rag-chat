FROM python:3.11-slim

# Set env. variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Not always needed (depends on the port) - should still work
EXPOSE 8000

# If the port is set as environment variable it is used, otherwise it defaults to 8000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}