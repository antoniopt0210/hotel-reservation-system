import os
import datetime
import stripe
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from db.postgres_client import db
from db.cassandra_client import (
    decrement_room_availability,
    increment_room_availability,
)
from models.booking import Booking
from models.room import Room
from utils.pricing import calculate_price, price_in_cents
from utils.email import (
    send_booking_confirmation,
    send_cancellation_confirmation,
)

bookings_bp = Blueprint('bookings', __name__)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')


def _redis():
    from db.redis_client import get_client
    return get_client()


def _lock_key(room_id, check_in, check_out):
    return f"booking_lock:{room_id}:{check_in}:{check_out}"


# ---------------------------------------------------------------------------
# Payment intent — step 1
# ---------------------------------------------------------------------------

@bookings_bp.route('/payment-intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    if not stripe.api_key:
        return jsonify({"error": "Payments not configured on this server."}), 503

    data      = request.get_json() or {}
    room_id   = data.get('room_id')
    check_in  = data.get('check_in')
    check_out = data.get('check_out')

    if not all([room_id, check_in, check_out]):
        return jsonify({"error": "room_id, check_in, and check_out are required."}), 400

    room = Room.query.get(room_id)
    if not room or not room.is_active:
        return jsonify({"error": "Room not found."}), 404

    try:
        ci = datetime.date.fromisoformat(check_in)
        co = datetime.date.fromisoformat(check_out)
    except ValueError:
        return jsonify({"error": "Dates must be YYYY-MM-DD."}), 400

    pricing = calculate_price(room, ci, co)

    # Try to acquire Redis lock (10-minute hold while user enters payment)
    try:
        r = _redis()
        lock_key = _lock_key(room_id, check_in, check_out)
        acquired = r.set(lock_key, get_jwt_identity(), nx=True, ex=600)
        if not acquired:
            return jsonify({"error": "This room is being reserved by another user. Please try again shortly."}), 409
    except Exception:
        pass  # Redis unavailable — skip lock, still functional for dev

    intent = stripe.PaymentIntent.create(
        amount=price_in_cents(pricing),
        currency='usd',
        metadata={
            'room_id':   room_id,
            'check_in':  check_in,
            'check_out': check_out,
            'user_id':   get_jwt_identity(),
        },
    )

    return jsonify({
        'client_secret':      intent.client_secret,
        'payment_intent_id':  intent.id,
        'pricing':            pricing,
        'room':               room.to_dict(),
        'hotel':              room.hotel.to_dict(),
    }), 200


# ---------------------------------------------------------------------------
# Confirm booking — step 2 (called after Stripe succeeds on frontend)
# ---------------------------------------------------------------------------

@bookings_bp.route('', methods=['POST'])
@jwt_required()
def confirm_booking():
    data               = request.get_json() or {}
    payment_intent_id  = data.get('payment_intent_id')
    room_id            = data.get('room_id')
    check_in           = data.get('check_in')
    check_out          = data.get('check_out')

    if not all([payment_intent_id, room_id, check_in, check_out]):
        return jsonify({"error": "payment_intent_id, room_id, check_in, check_out required."}), 400

    # Verify payment with Stripe — never trust the frontend
    if stripe.api_key:
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if intent.status != 'succeeded':
                return jsonify({"error": "Payment not completed."}), 402
            if (intent.metadata.get('room_id')  != room_id or
                    intent.metadata.get('user_id') != get_jwt_identity()):
                return jsonify({"error": "Payment intent mismatch."}), 400
        except stripe.error.StripeError as e:
            return jsonify({"error": str(e)}), 400

    room = Room.query.get(room_id)
    if not room:
        return jsonify({"error": "Room not found."}), 404

    ci = datetime.date.fromisoformat(check_in)
    co = datetime.date.fromisoformat(check_out)
    pricing = calculate_price(room, ci, co)

    booking = Booking(
        user_id           = get_jwt_identity(),
        room_id           = room_id,
        hotel_id          = room.hotel_id,
        check_in_date     = ci,
        check_out_date    = co,
        guest_first_name  = data.get('first_name', ''),
        guest_last_name   = data.get('last_name', ''),
        guest_email       = data.get('email', ''),
        num_guests        = data.get('num_guests', 1),
        special_requests  = data.get('special_requests'),
        total_price_usd   = pricing['total'],
        stripe_payment_id = payment_intent_id,
        status            = 'confirmed',
    )
    db.session.add(booking)
    db.session.commit()

    # Decrement Cassandra availability
    try:
        decrement_room_availability(room_id, ci, co, room.total_units)
    except Exception as e:
        print(f"[availability] Failed to decrement: {e}")

    # Release Redis lock
    try:
        _redis().delete(_lock_key(room_id, check_in, check_out))
    except Exception:
        pass

    # Send confirmation email (non-blocking)
    try:
        send_booking_confirmation(booking, room, room.hotel)
    except Exception as e:
        print(f"[email] Confirmation failed: {e}")

    return jsonify({"booking": booking.to_dict()}), 201


# ---------------------------------------------------------------------------
# Read bookings
# ---------------------------------------------------------------------------

@bookings_bp.route('/mine', methods=['GET'])
@jwt_required()
def my_bookings():
    bookings = (
        Booking.query
        .filter_by(user_id=get_jwt_identity())
        .order_by(Booking.created_at.desc())
        .all()
    )
    return jsonify({"bookings": [b.to_dict() for b in bookings]}), 200


@bookings_bp.route('/<booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found."}), 404
    if booking.user_id != get_jwt_identity():
        return jsonify({"error": "Access denied."}), 403
    return jsonify({"booking": booking.to_dict()}), 200


# ---------------------------------------------------------------------------
# Cancel
# ---------------------------------------------------------------------------

@bookings_bp.route('/<booking_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found."}), 404
    if booking.user_id != get_jwt_identity():
        return jsonify({"error": "Access denied."}), 403
    if booking.status in ('cancelled', 'checked_out'):
        return jsonify({"error": f"Cannot cancel a {booking.status} booking."}), 400

    data   = request.get_json() or {}
    reason = data.get('reason', '')

    booking.status              = 'cancelled'
    booking.cancelled_at        = datetime.datetime.utcnow()
    booking.cancellation_reason = reason
    db.session.commit()

    # Restore Cassandra availability
    try:
        room = Room.query.get(booking.room_id)
        if room:
            increment_room_availability(
                booking.room_id,
                booking.check_in_date,
                booking.check_out_date,
                room.total_units,
            )
    except Exception as e:
        print(f"[availability] Failed to restore on cancel: {e}")

    try:
        send_cancellation_confirmation(booking, booking.hotel)
    except Exception:
        pass

    return jsonify({"booking": booking.to_dict()}), 200
