from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from db.postgres_client import db
from models.wishlist import WishlistItem
from models.hotel import Hotel

wishlist_bp = Blueprint('wishlist', __name__)


@wishlist_bp.route('', methods=['GET'])
@jwt_required()
def get_wishlist():
    user_id = get_jwt_identity()
    items = WishlistItem.query.filter_by(user_id=user_id).order_by(WishlistItem.added_at.desc()).all()
    return jsonify({
        'wishlist': [{
            'id':       item.id,
            'hotel_id': item.hotel_id,
            'hotel':    item.hotel.to_dict() if item.hotel else None,
            'added_at': str(item.added_at),
        } for item in items]
    })


@wishlist_bp.route('/<hotel_id>', methods=['POST'])
@jwt_required()
def add_to_wishlist(hotel_id):
    user_id = get_jwt_identity()

    hotel = Hotel.query.get(hotel_id)
    if not hotel:
        return jsonify({'error': 'Hotel not found'}), 404

    existing = WishlistItem.query.filter_by(user_id=user_id, hotel_id=hotel_id).first()
    if existing:
        return jsonify({'message': 'Already in wishlist', 'id': existing.id}), 200

    item = WishlistItem(user_id=user_id, hotel_id=hotel_id)
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Added to wishlist', 'id': item.id}), 201


@wishlist_bp.route('/<hotel_id>', methods=['DELETE'])
@jwt_required()
def remove_from_wishlist(hotel_id):
    user_id = get_jwt_identity()
    item = WishlistItem.query.filter_by(user_id=user_id, hotel_id=hotel_id).first()
    if not item:
        return jsonify({'error': 'Not in wishlist'}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Removed from wishlist'}), 200
