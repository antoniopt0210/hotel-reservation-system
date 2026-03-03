from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime

from cassandra_db import (
    create_reservation as db_create_reservation,
    get_all_reservations,
    update_reservation_status,
    delete_reservation,
)

# Create Flask application instance
app = Flask(__name__)

# enable CORS for all routes and origin
CORS(app)


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
        return {"error": f"Missing required field: {str(e)}"}, 400
    except ValueError as e:
        return {"error": str(e)}, 400
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}, 500


# Retrieve all reservations
@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    try:
        reservations_list = get_all_reservations()
        return jsonify({"reservations": reservations_list}), 200
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500


# Modify an existing reservation
@app.route('/api/reservations/<reservation_id>', methods=['PUT', 'DELETE'])
def update_or_delete_reservation(reservation_id):
    if request.method == 'PUT':
        try:
            data = request.get_json()
            new_status = data.get('status')

            if not update_reservation_status(reservation_id, new_status):
                return {"message": "Reservation not found"}, 404
            return {"message": "Reservation modified successfully"}, 200
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500

    elif request.method == 'DELETE':
        try:
            if not delete_reservation(reservation_id):
                return {"message": "Reservation not found"}, 404
            return {"message": "Reservation deleted successfully"}, 200
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500


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
