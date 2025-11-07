#!/bin/bash
# Start the FastAPI application using uvicorn
# This script is used by Azure App Service
export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH
cd /home/site/wwwroot
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}