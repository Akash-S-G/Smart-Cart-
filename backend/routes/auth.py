from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

auth = Blueprint('auth', __name__)

# Simulated user database for demo purposes
users = {}

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    email = data['email']
    if email in users:
        return jsonify({'message': 'Email already registered'}), 400
    
    users[email] = {
        'name': data['name'],
        'password': generate_password_hash(data['password']),
        'role': 'user'
    }
    
    access_token = create_access_token(
        identity=email,
        additional_claims={'name': data['name'], 'role': 'user'}
    )
    
    return jsonify({
        'message': 'User registered successfully',
        'token': access_token
    }), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
    
    email = data['email']
    user = users.get(email)
    
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    access_token = create_access_token(
        identity=email,
        additional_claims={'name': user['name'], 'role': user['role']}
    )
    
    return jsonify({
        'message': 'Login successful',
        'token': access_token
    }), 200

@auth.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    user = users.get(current_user)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'email': current_user,
        'name': user['name'],
        'role': user['role']
    }) 