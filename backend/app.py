from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime

from cassandra_db import (
    create_reservation as db_create_reservation,
    get_all_reservations,
    update_reservation_status,
    delete_reservation,
    get_session,
)

# Create Flask application instance
app = Flask(__name__)

# enable CORS for all routes and origin
CORS(app)


# Health check - no DB required (for Render port detection)
@app.route('/')
@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "message": "Hotel Reservation API"}), 200


# Connection check - verifies Render can reach Astra
@app.route('/api/db-check')
def db_check():
    """Test if the app can connect to Cassandra/Astra. Use this to verify Render → Astra connectivity."""
    try:
        session = get_session()
        # Run a simple query to verify connection
        session.execute("SELECT release_version FROM system.local")
        return jsonify({
            "status": "connected",
            "message": "Successfully connected to Cassandra/Astra",
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Failed to connect to Cassandra/Astra",
            "error": str(e),
        }), 503


# Create reservation
@app.route('/api/reservations', methods=['POST'])
def create_reservation():
    try:
        data = request.get_json()
        print("Received reservation data:")
        print(data)

        # Validate check-in and check-out dates
        is_valid, message = validate_reservation_dates(data['check_in_date'], data['check_out_date'])
        if not is_valid:
            raise ValueError(message)

        reservation = db_create_reservation(data)
        return {"message": "Reservation Booked!", "reservation": reservation}, 201
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


# Retrieve all reservations
@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    try:
        reservations_list = get_all_reservations()
        return jsonify({"reservations": reservations_list}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Modify an existing reservation
@app.route('/api/reservations/<reservation_id>', methods=['PUT', 'DELETE'])
def update_or_delete_reservation(reservation_id):
    if request.method == 'PUT':
        try:
            data = request.get_json()
            new_status = data.get('status')

            if not update_reservation_status(reservation_id, new_status):
                return jsonify({"message": "Reservation not found"}), 404
            return jsonify({"message": "Reservation modified successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    elif request.method == 'DELETE':
        try:
            if not delete_reservation(reservation_id):
                return jsonify({"message": "Reservation not found"}), 404
            return jsonify({"message": "Reservation deleted successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500


def validate_reservation_dates(checkin, checkout):
    now = datetime.datetime.now().date()
    checkin_date = datetime.datetime.strptime(checkin, '%Y-%m-%d').date()
    checkout_date = datetime.datetime.strptime(checkout, '%Y-%m-%d').date()

    if checkin_date < now or checkout_date < now:
        return False, "Check-in and check-out dates must be in the future."
    if checkout_date <= checkin_date:
        return False, "Check-out date must be after check-in date."

    return True, ""


# Run app
if __name__ == "__main__":
    app.run(debug=True)
