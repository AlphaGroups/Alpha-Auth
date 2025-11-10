#!/bin/bash
# Start the FastAPI application using gunicorn with uvicorn worker
# This script is used by Azure App Service
export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH
cd /home/site/wwwroot

# Check if gunicorn is available, otherwise use uvicorn directly
if command -v gunicorn &> /dev/null
then
    exec gunicorn --config gunicorn.conf.py main:app
else
    exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
fi