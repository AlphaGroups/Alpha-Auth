import os

# Gunicorn configuration file
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
max_requests = 1000
max_requests_jitter = 100