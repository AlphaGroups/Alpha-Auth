# Dockerfile

FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose FastAPI port - using standard port 8000
EXPOSE 8000

# Run the FastAPI server using the PORT environment variable (for Azure)
CMD ["sh", "-c", "gunicorn --config gunicorn.conf.py main:app"]
