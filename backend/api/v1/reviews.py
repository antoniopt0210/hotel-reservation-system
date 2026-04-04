from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

from db.postgres_client import db
from models.hotel import Hotel
from models.booking import Booking
from models.review import Review

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/hotels/<hotel_id>/reviews', methods=['GET'])
def list_reviews(hotel_id):
    """Return paginated reviews for a hotel, newest first."""
    page     = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 10)), 50)

    q = (
        Review.query
        .filter_by(hotel_id=hotel_id)
        .order_by(Review.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify({
        'reviews':    [r.to_dict() for r in q.items],
        'total':      q.total,
        'page':       page,
        'pages':      q.pages,
        'per_page':   per_page,
    })


@reviews_bp.route('/hotels/<hotel_id>/reviews', methods=['POST'])
@jwt_required()
def create_review(hotel_id):
    """Submit a review. Must have a completed booking at this hotel."""
    user_id = get_jwt_identity()
    data    = request.get_json() or {}

    hotel = Hotel.query.get(hotel_id)
    if not hotel:
        return jsonify({'error': 'Hotel not found'}), 404

    rating = data.get('rating')
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': 'rating must be an integer 1–5'}), 400

    # Check the user has a checked_out booking at this hotel (or confirmed — allow early)
    booking = Booking.query.filter(
        Booking.hotel_id  == hotel_id,
        Booking.user_id   == user_id,
        Booking.status.in_(['confirmed', 'checked_in', 'checked_out']),
    ).first()
    if not booking:
        return jsonify({'error': 'You must have a booking at this hotel to leave a review'}), 403

    # One review per booking
    if booking.review:
        return jsonify({'error': 'You have already reviewed this booking'}), 409

    review = Review(
        hotel_id   = hotel_id,
        booking_id = booking.id,
        user_id    = user_id,
        rating     = rating,
        title      = (data.get('title') or '')[:120],
        body       = data.get('body') or '',
    )
    db.session.add(review)
    db.session.commit()

    return jsonify({'review': review.to_dict()}), 201


@reviews_bp.route('/reviews/<review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """Delete own review (or any review if superadmin)."""
    from models.user import User
    user_id = get_jwt_identity()
    review  = Review.query.get_or_404(review_id)
    user    = User.query.get(user_id)

    if review.user_id != user_id and (not user or user.role != 'superadmin'):
        return jsonify({'error': 'Forbidden'}), 403

    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Review deleted'}), 200


@reviews_bp.route('/hotels/<hotel_id>/reviews/summary', methods=['GET'])
def review_summary(hotel_id):
    """Return rating breakdown (1–5 star counts) for a hotel."""
    reviews = Review.query.filter_by(hotel_id=hotel_id).all()
    counts  = {str(i): 0 for i in range(1, 6)}
    for rv in reviews:
        counts[str(rv.rating)] = counts.get(str(rv.rating), 0) + 1

    total  = len(reviews)
    avg    = round(sum(rv.rating for rv in reviews) / total, 1) if total else None

    return jsonify({
        'total':      total,
        'avg_rating': avg,
        'breakdown':  counts,
    })
