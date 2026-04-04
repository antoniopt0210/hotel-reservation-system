from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from db.postgres_client import db
from models.user import User
from models.hotel import Hotel
from models.room import Room
from models.booking import Booking
from models.review import Review
from utils.auth_helpers import admin_required, superadmin_required

admin_bp = Blueprint('admin', __name__)


# ---------------------------------------------------------------------------
# Dashboard stats
# ---------------------------------------------------------------------------

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def dashboard_stats():
    user = User.query.get(get_jwt_identity())
    is_super = user.role == 'superadmin'

    if is_super:
        bookings_q = Booking.query
        hotels_q   = Hotel.query
        rooms_q    = Room.query
        reviews_q  = Review.query
    else:
        owned_ids  = [h.id for h in Hotel.query.filter_by(owner_user_id=user.id).all()]
        bookings_q = Booking.query.filter(Booking.hotel_id.in_(owned_ids))
        hotels_q   = Hotel.query.filter(Hotel.id.in_(owned_ids))
        rooms_q    = Room.query.filter(Room.hotel_id.in_(owned_ids))
        reviews_q  = Review.query.filter(Review.hotel_id.in_(owned_ids))

    total_bookings  = bookings_q.count()
    confirmed       = bookings_q.filter_by(status='confirmed').count()
    cancelled       = bookings_q.filter_by(status='cancelled').count()
    revenue         = db.session.query(
        db.func.coalesce(db.func.sum(Booking.total_price_usd), 0)
    ).filter(
        Booking.status.in_(['confirmed', 'checked_in', 'checked_out']),
        *([Booking.hotel_id.in_([h.id for h in hotels_q.all()])] if not is_super else [])
    ).scalar()

    return jsonify({
        'total_hotels':    hotels_q.count(),
        'total_rooms':     rooms_q.count(),
        'total_bookings':  total_bookings,
        'confirmed':       confirmed,
        'cancelled':       cancelled,
        'total_revenue':   float(revenue),
        'total_reviews':   reviews_q.count(),
        'total_users':     User.query.count() if is_super else None,
    })


# ---------------------------------------------------------------------------
# Bookings management
# ---------------------------------------------------------------------------

@admin_bp.route('/bookings', methods=['GET'])
@admin_required
def list_bookings():
    user     = User.query.get(get_jwt_identity())
    is_super = user.role == 'superadmin'

    page     = max(int(request.args.get('page', 1)), 1)
    per_page = min(int(request.args.get('per_page', 20)), 50)
    status   = request.args.get('status')

    query = Booking.query
    if not is_super:
        owned_ids = [h.id for h in Hotel.query.filter_by(owner_user_id=user.id).all()]
        query = query.filter(Booking.hotel_id.in_(owned_ids))

    if status:
        query = query.filter_by(status=status)

    query = query.order_by(Booking.created_at.desc())
    pag   = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'bookings': [b.to_dict() for b in pag.items],
        'total':    pag.total,
        'page':     page,
        'pages':    pag.pages,
    })


@admin_bp.route('/bookings/<booking_id>/status', methods=['PUT'])
@admin_required
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    user     = User.query.get(get_jwt_identity())
    is_super = user.role == 'superadmin'
    if not is_super:
        hotel = Hotel.query.get(booking.hotel_id)
        if not hotel or hotel.owner_user_id != user.id:
            return jsonify({'error': 'Forbidden'}), 403

    data       = request.get_json() or {}
    new_status = data.get('status')
    if new_status not in Booking.STATUSES:
        return jsonify({'error': f'Invalid status. Must be one of {Booking.STATUSES}'}), 400

    booking.status = new_status
    db.session.commit()
    return jsonify({'booking': booking.to_dict()})


# ---------------------------------------------------------------------------
# Users management (superadmin only)
# ---------------------------------------------------------------------------

@admin_bp.route('/users', methods=['GET'])
@superadmin_required
def list_users():
    page     = max(int(request.args.get('page', 1)), 1)
    per_page = min(int(request.args.get('per_page', 20)), 50)

    pag = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'users': [{
            'id':         u.id,
            'first_name': u.first_name,
            'last_name':  u.last_name,
            'email':      u.email,
            'role':       u.role,
            'created_at': str(u.created_at),
        } for u in pag.items],
        'total': pag.total,
        'page':  page,
        'pages': pag.pages,
    })


@admin_bp.route('/users/<user_id>/role', methods=['PUT'])
@superadmin_required
def update_user_role(user_id):
    target = User.query.get_or_404(user_id)
    data   = request.get_json() or {}
    role   = data.get('role')
    if role not in ('guest', 'hotel_admin', 'superadmin'):
        return jsonify({'error': 'Invalid role'}), 400
    target.role = role
    db.session.commit()
    return jsonify({'message': f'Role updated to {role}'})
