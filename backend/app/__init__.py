from flask import Flask
from flask_cors import CORS
from backend.config import Config
from backend.app.extensions import init_pipeline

def create_app(config_class=Config):
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})

    # Load machine learning models exactly once at startup
    init_pipeline()

    # Register blueprints
    from backend.app.api.routes import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    # Add security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    return app
