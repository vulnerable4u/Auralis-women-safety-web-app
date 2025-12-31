# Procfile for Render Deployment
# Build command: Creates virtual environment and installs dependencies
build: ./build.sh

# Web service command: Run with gunicorn using gthread workers for ML/audio workloads
# - gthread: Thread-based workers, better for TensorFlow/librosa/Supabase
# - 2 workers with 8 threads each: Balanced for ML workloads with shared memory
# - timeout 300: Longer timeout for ML model inference
# - keepalive 5: Connection keep-alive for HTTP/1.1
# - max-requests 1000: Recycle workers after 1000 requests to prevent memory leaks
# - access/error log to stdout: Required for Render logs
web: source venv/bin/activate && gunicorn Backend.wsgi:app --bind 0.0.0.0:$PORT --workers 2 --threads 8 --worker-class gthread --timeout 300 --keepalive 5 --max-requests 1000 --max-requests-jitter 50 --access-logfile - --error-logfile -

