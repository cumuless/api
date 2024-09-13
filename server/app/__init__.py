from flask import Flask
from flask_cors import CORS
from server.config.config import Config
from flask_cognito import CognitoAuth

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CognitoAuth(app)
    # Enable CORS
    CORS(app)

    # Register blueprints
    from server.app.routes.main import main_bp

    app.register_blueprint(main_bp)

    return app
