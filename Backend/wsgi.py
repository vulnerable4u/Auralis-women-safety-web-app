"""
Production WSGI Entry Point for Render Deployment
Optimized for Gunicorn with gevent workers for async I/O
"""

import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

# Ensure we use the virtual environment's site-packages
# This is critical for Render deployment to avoid externally-managed-environment errors
VENV_PATH = os.path.join(PROJECT_ROOT, "venv")
if os.path.exists(VENV_PATH):
    venv_site_packages = os.path.join(VENV_PATH, "lib")
    # Find the python version directory
    for item in os.listdir(venv_site_packages):
        if item.startswith("python"):
            site_packages = os.path.join(venv_site_packages, item, "site-packages")
            if os.path.exists(site_packages):
                sys.path.insert(0, site_packages)
                break

import json
import logging
from datetime import datetime, timezone
from uuid import uuid4
import structlog

# =========================================================
# STRUCTURED JSON LOGGING CONFIGURATION
# =========================================================

def setup_structured_logging():
    """Configure structlog for production JSON logs"""
    
    # Pre-process log entries to add standard fields
    def add_timestamp(logger, method_name, event_dict):
        event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
        return event_dict
    
    def add_request_id(logger, method_name, event_dict):
        if "request_id" not in event_dict:
            event_dict["request_id"] = "N/A"
        return event_dict
    
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            add_timestamp,
            add_request_id,
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True
    )
    
    # Configure Python stdlib logging
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

setup_structured_logging()

logger = structlog.get_logger(__name__)

# =========================================================
# FLASK APPLICATION FACTORY
# =========================================================

def create_app():
    """Application factory with production settings"""
    
    # Import Flask after logging is configured
    from flask import Flask, g, request
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Define paths
    FRONTEND_DIR = os.path.join(PROJECT_ROOT, "Frontend")
    
    # Production Flask configuration
    app = Flask(
        __name__,
        template_folder=os.path.join(FRONTEND_DIR, "templates"),
        static_folder=os.path.join(FRONTEND_DIR, "static")
    )
    
    # Security settings
    app.secret_key = os.environ.get("SECRET_KEY")
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    
    # Disable debug in production
    app.config["DEBUG"] = False
    app.config["TESTING"] = False
    
    # Request ID middleware
    @app.before_request
    def before_request():
        g.request_id = request.headers.get("X-Request-ID", str(uuid4()))
        g.start_time = datetime.now(timezone.utc)
    
    @app.after_request
    def after_request(response):
        # Add request ID to response headers
        response.headers["X-Request-ID"] = g.get("request_id", "N/A")
        
        # Log request duration
        if hasattr(g, "start_time"):
            duration = (datetime.now(timezone.utc) - g.start_time).total_seconds()
            logger.info(
                "request_completed",
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
                request_id=g.request_id
            )
        
        return response
    
    # Import and register routes
    from server_backend import app as backend_app
    
    # Copy routes from backend app
    for rule in backend_app.url_map.iter_rules():
        endpoint = rule.endpoint
        if hasattr(backend_app, endpoint):
            view_func = getattr(backend_app, endpoint)
            app.add_url_rule(rule.rule, endpoint, view_func, methods=rule.methods)
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return {"error": "Bad request", "request_id": g.get("request_id")}, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {"error": "Unauthorized", "request_id": g.get("request_id")}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {"error": "Forbidden", "request_id": g.get("request_id")}, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found", "request_id": g.get("request_id")}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error("internal_error", request_id=g.get("request_id"), error=str(error))
        return {"error": "Internal server error", "request_id": g.get("request_id")}, 500
    
    logger.info("flask_app_created", production=True)
    
    return app

# Create application instance
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))

