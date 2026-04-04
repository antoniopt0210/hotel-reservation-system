import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from db.postgres_client import db
from models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    required = ('email', 'password', 'first_name', 'last_name')
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if User.query.filter_by(email=data['email'].lower()).first():
        return jsonify({"error": "Email already registered"}), 409

    pw_hash = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()

    user = User(
        email=data['email'].lower(),
        password_hash=pw_hash,
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data.get('phone'),
    )
    db.session.add(user)
    db.session.commit()

    access_token  = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        "user":          user.to_dict(),
        "access_token":  access_token,
        "refresh_token": refresh_token,
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email    = data.get('email', '').lower()
    password = data.get('password', '')

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token  = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        "user":          user.to_dict(),
        "access_token":  access_token,
        "refresh_token": refresh_token,
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    access_token = create_access_token(identity=get_jwt_identity())
    return jsonify({"access_token": access_token}), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Stateless JWT — client simply discards the token.
    # Token blocklist (Redis) added in Phase 3.
    return jsonify({"message": "Logged out"}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200


@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json() or {}

    if 'first_name' in data and data['first_name'].strip():
        user.first_name = data['first_name'].strip()
    if 'last_name' in data and data['last_name'].strip():
        user.last_name = data['last_name'].strip()
    if 'phone' in data:
        user.phone = data['phone'].strip() or None

    if data.get('new_password'):
        if not data.get('current_password'):
            return jsonify({"error": "Current password is required"}), 400
        if not bcrypt.checkpw(data['current_password'].encode(), user.password_hash.encode()):
            return jsonify({"error": "Current password is incorrect"}), 401
        user.password_hash = bcrypt.hashpw(data['new_password'].encode(), bcrypt.gensalt()).decode()

    db.session.commit()
    return jsonify({"user": user.to_dict(), "message": "Profile updated"}), 200
