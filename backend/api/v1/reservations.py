from flask import Blueprint, request, jsonify

from db.cassandra_client import (
    create_reservation as db_create_reservation,
    get_all_reservations,
    update_reservation_status,
    delete_reservation,
)
from utils.validators import validate_reservation_dates

reservations_bp = Blueprint('reservations', __name__)


@reservations_bp.route('', methods=['POST'])
def create_reservation():
    try:
        data = request.get_json()

        is_valid, message = validate_reservation_dates(
            data['check_in_date'], data['check_out_date']
        )
        if not is_valid:
            return jsonify({"error": message}), 400

        reservation = db_create_reservation(data)
        return jsonify({"message": "Reservation Booked!", "reservation": reservation}), 201

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@reservations_bp.route('', methods=['GET'])
def get_reservations():
    try:
        reservations_list = get_all_reservations()
        return jsonify({"reservations": reservations_list}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@reservations_bp.route('/<reservation_id>', methods=['PUT'])
def update_reservation(reservation_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        check_in_date = data.get('check_in_date')  # optional; speeds up partition lookup

        if not update_reservation_status(reservation_id, new_status, check_in_date):
            return jsonify({"message": "Reservation not found"}), 404
        return jsonify({"message": "Reservation modified successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@reservations_bp.route('/<reservation_id>', methods=['DELETE'])
def delete_reservation_route(reservation_id):
    try:
        check_in_date = request.args.get('check_in_date')  # optional query param

        if not delete_reservation(reservation_id, check_in_date):
            return jsonify({"message": "Reservation not found"}), 404
        return jsonify({"message": "Reservation deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
