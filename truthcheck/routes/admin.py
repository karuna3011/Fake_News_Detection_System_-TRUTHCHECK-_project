from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import db
from models.user import User
from models.prediction import Prediction
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard():
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_predictions = Prediction.query.count()
    fake_predictions = Prediction.query.filter_by(result='FAKE').count()
    real_predictions = Prediction.query.filter_by(result='REAL').count()

    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'total_predictions': total_predictions,
        'fake_predictions': fake_predictions,
        'real_predictions': real_predictions,
    })

@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
    return jsonify({
        'users': [u.to_dict() for u in users.items],
        'total': users.total,
        'pages': users.pages,
    })

@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        return jsonify({'error': 'Cannot deactivate admin'}), 400
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'message': f"User {'activated' if user.is_active else 'deactivated'}", 'user': user.to_dict()})

@admin_bp.route('/predictions', methods=['GET'])
@admin_required
def list_predictions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    preds = Prediction.query.order_by(Prediction.created_at.desc()).paginate(page=page, per_page=per_page)
    return jsonify({
        'predictions': [p.to_dict() for p in preds.items],
        'total': preds.total,
        'pages': preds.pages,
    })
