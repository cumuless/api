from flask import Blueprint
from flask_cognito import cognito_auth_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return "Hello, World!"

@main_bp.route('/protected')
@cognito_auth_required
def protected():
    return "This is a protected route."
