# Use the PORT environment variable provided by Azure App Service
# If not available, default to 8000
PORT=${PORT:-8000}
echo "Starting application on port $PORT"

# Install any missing dependencies
pip install -r requirements.txt

# Start the application with uvicorn
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4