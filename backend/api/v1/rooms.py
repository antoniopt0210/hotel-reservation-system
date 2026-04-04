import datetime
from flask import Blueprint, request, jsonify
from db.cassandra_client import get_room_availability_month
from utils.auth_helpers import admin_required

rooms_bp = Blueprint('rooms', __name__)


@rooms_bp.route('/<room_id>/availability', methods=['GET'])
def get_availability(room_id):
    """
    Return availability data for a room for a given month.
    Query param: ?month=YYYY-MM  (defaults to current month)
    """
    month = request.args.get('month', datetime.date.today().strftime('%Y-%m'))
    try:
        rows = get_room_availability_month(room_id, month)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"room_id": room_id, "month": month, "availability": rows}), 200


@rooms_bp.route('/<room_id>/pricing', methods=['PUT'])
@admin_required
def set_price_overrides(room_id):
    """
    Set per-night price overrides for a room.
    Body: { "overrides": [ {"date": "2026-06-15", "price": 299.00}, ... ] }
    Pass price=null to remove the override for that night.
    """
    data = request.get_json() or {}
    overrides = data.get('overrides', [])
    if not overrides:
        return jsonify({"error": "No overrides provided"}), 400

    try:
        from db.cassandra_client import get_session, KEYSPACE
        session = get_session()
        session.set_keyspace(KEYSPACE)

        for entry in overrides:
            date_str = entry.get('date')
            price = entry.get('price')
            if not date_str:
                continue
            d = datetime.date.fromisoformat(date_str)
            ym = d.strftime('%Y-%m')

            if price is None:
                # Remove override — set price_override to null
                session.execute(
                    "UPDATE room_availability SET price_override = null "
                    "WHERE room_id = %s AND year_month = %s AND stay_date = %s",
                    (room_id, ym, date_str)
                )
            else:
                from decimal import Decimal
                session.execute(
                    "INSERT INTO room_availability (room_id, year_month, stay_date, price_override) "
                    "VALUES (%s, %s, %s, %s)",
                    (room_id, ym, date_str, Decimal(str(price)))
                )

        return jsonify({"message": f"{len(overrides)} price override(s) applied"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
