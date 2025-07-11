# Use an official Python image
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source code
COPY . .

# Use environment variables from .env
ENV PYTHONUNBUFFERED=1

# Default command — we can override this in docker-compose
CMD ["python", "src/main.py"]
