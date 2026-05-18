from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import (
    create_access_token, jwt_required,
    get_jwt_identity, create_refresh_token
)
from datetime import datetime, timedelta
from database.db import db
from models.user import User
import re, logging

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
logger = logging.getLogger(__name__)

def _validate_email(email):
    return re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email) is not None

def _validate_password(pw):
    return len(pw) >= 8

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    if not _validate_email(email):
        return jsonify({'error': 'Invalid email address'}), 400
    if not _validate_password(password):
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=24))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'message': 'Account created successfully!',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated. Contact support.'}), 403

    user.last_login = datetime.utcnow()
    db.session.commit()

    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=24))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'message': 'Login successful!',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    })

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()})

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id, expires_delta=timedelta(hours=24))
    return jsonify({'access_token': access_token})
