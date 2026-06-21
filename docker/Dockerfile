# Use official Python 3.11 slim image (smaller size, faster build)

FROM python:3.11-slim
 
# Set working directory inside the container

WORKDIR /app
 
# Install system dependencies needed by psycopg2

RUN apt-get update && apt-get install -y \

    gcc \

    libpq-dev \
&& rm -rf /var/lib/apt/lists/*
 
# Copy requirements first (Docker caches this layer)

# If requirements.txt hasn't changed, Docker skips reinstalling

COPY requirements.txt .
 
# Install Python dependencies

RUN pip install --no-cache-dir -r requirements.txt
 
# Copy the entire project into the container

COPY . .
 
# Expose port 8000

EXPOSE 8000
 
# Command to run the app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
 