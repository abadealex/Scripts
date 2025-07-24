# api/v1/auth.py
from flask import Blueprint, request, jsonify

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Dummy user store for demonstration
users = {}

@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    if username in users:
        return jsonify({'error': 'User already exists'}), 409
    # In a real app, hash password & save user in DB
    users[username] = password
    return jsonify({'message': 'User registered successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    stored_password = users.get(username)
    if stored_password is None or stored_password != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    # Normally, generate and return auth token (JWT etc.)
    return jsonify({'message': 'Login successful', 'token': 'dummy-token'}), 200
