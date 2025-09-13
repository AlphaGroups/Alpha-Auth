# # Dockerfile

# FROM python:3.11-slim

# # Set working directory
# WORKDIR /app

# # Install dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy entire project
# COPY . .

# # Expose FastAPI port
# EXPOSE 8000

# # Run the FastAPI server
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9080", "--reload"]


# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for MySQL, cryptography, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose FastAPI port (match with Render PORT)
EXPOSE 10000

# Run the FastAPI server (no reload in prod)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
