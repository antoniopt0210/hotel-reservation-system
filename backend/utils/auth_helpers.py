from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request


def admin_required(fn):
    """Decorator: requires hotel_admin or superadmin role."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        from models.user import User
        user = User.query.get(get_jwt_identity())
        if not user or user.role not in ('hotel_admin', 'superadmin'):
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


def superadmin_required(fn):
    """Decorator: requires superadmin role."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        from models.user import User
        user = User.query.get(get_jwt_identity())
        if not user or user.role != 'superadmin':
            return jsonify({"error": "Superadmin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper
