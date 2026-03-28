import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    from app.routes.brand import brand_bp
    from app.routes.health import health_bp

    app.register_blueprint(brand_bp, url_prefix="/api/v1/brand")
    app.register_blueprint(health_bp, url_prefix="/api/v1")

    return app
