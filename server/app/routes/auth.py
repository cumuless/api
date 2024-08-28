from flask import Blueprint, request, jsonify
from server.app.services.cognito_service import CognitoService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    token = CognitoService.authenticate(username, password)
    if token:
        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
