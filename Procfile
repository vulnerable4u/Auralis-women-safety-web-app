# Procfile for Render Deployment
# Build command: Creates virtual environment and installs dependencies
build: ./build.sh

# Web service command: Run with gunicorn using the virtual environment
web: source venv/bin/activate && gunicorn Backend.wsgi:app --bind 0.0.0.0:$PORT --workers 4 --worker-class gevent --timeout 120 --access-logfile - --error-logfile -

