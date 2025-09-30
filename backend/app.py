from flask import Flask, request, g, jsonify
from flask_cors import CORS
import sqlite3
import datetime

# Create Flask application instance
app = Flask(__name__)

# enable CORS for all routes and origin
CORS(app)

DATABASE = 'reservations.db'

# Function to get a new database connection
def get_db_connection():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

# A teardown function that closes the database connection automatically
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize a database table
def init_db():
    with app.app_context():
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                birthday TEXT,
                check_in_date TEXT NOT NULL,
                check_out_date TEXT NOT NULL,
                room_type TEXT NOT NULL,
                extra_info TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            '''
        )
        db.commit()

init_db()

# Create reservation
@app.route('/api/reservations', methods=['POST'])
def create_reservation():
    try:
        data = request.get_json()
        print("Received reservation data:")
        print(data)
        
        db = get_db_connection()
        cursor = db.cursor()

        # Validate check-in and check-out dates
        is_valid, message = validate_reservation_dates(data['check_in_date'], data['check_out_date'])
        if not is_valid:
            raise ValueError({"error": message})

        cursor.execute(
            '''
            INSERT INTO reservations (
                first_name, 
                last_name, 
                birthday,
                check_in_date,
                check_out_date,
                room_type,
                extra_info,
                status,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            ''', (
                data['first_name'],
                data['last_name'],
                data['birthday'],
                data['check_in_date'],
                data['check_out_date'],
                data['room_type'],
                data['extra_info'],
                data['status'],
                data['created_at']
            )
        )
        db.commit()

        return {"message": "Reservation Booked!", "reservation": data}, 201
    except KeyError as e:
        return {"error": f"Missing required field: {str(e)}"}, 400
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}, 500


# Retrieve all reservations
@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    try:
        db = get_db_connection()
        cursor = db.cursor()

        # execute SQL query to select all reservations
        cursor.execute(
            "SELECT * FROM reservations;"
        )
        rows = cursor.fetchall()

        # convert the rows into a list of dictionaries for JSON serialization
        reservations_list = [dict(row) for row in rows]

        return jsonify({"reservations": reservations_list}), 200
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, 500

# Modify an existing reservation
@app.route('/api/reservations/<int:reservation_id>', methods=['PUT', 'DELETE'])
def update_or_delete_reservation(reservation_id):
    db = get_db_connection()
    cursor = db.cursor()

    if request.method == 'PUT':
        try:
            data = request.get_json()
            new_status = data.get('status')

            # update status of the reservation
            cursor.execute(
                "UPDATE reservations SET status = ? WHERE id = ?;",
                (new_status, reservation_id)
            )
            db.commit()

            if cursor.rowcount == 0:
                return {"message": "Reservation not found"}, 404
            return {"message": "Reservation modified successfully"}, 200
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500
        
    elif request.method == 'DELETE':
        try:
            # cancel the reservation
            cursor.execute("DELETE FROM reservations WHERE id = ?;", 
                           (reservation_id,)
            )
            db.commit()
            
            if cursor.rowcount == 0:
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
