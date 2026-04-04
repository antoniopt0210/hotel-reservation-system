import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import config


def create_app(config_name: str = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    CORS(app)
    JWTManager(app)

    # ------------------------------------------------------------------ #
    # PostgreSQL — only initialised when DATABASE_URL is set
    # ------------------------------------------------------------------ #
    if os.environ.get('DATABASE_URL'):
        from db.postgres_client import init_app as init_postgres, db
        init_postgres(app)
        with app.app_context():
            import models  # noqa: F401 — registers all models with SQLAlchemy
            db.create_all()

    # ------------------------------------------------------------------ #
    # Email (Flask-Mail) — only when MAIL_PASSWORD is set
    # ------------------------------------------------------------------ #
    if os.environ.get('MAIL_PASSWORD'):
        from utils.email import init_app as init_mail
        init_mail(app)

    # ------------------------------------------------------------------ #
    # Blueprints
    # ------------------------------------------------------------------ #
    from api.v1.reservations import reservations_bp
    from api.v1.auth import auth_bp
    from api.v1.hotels import hotels_bp
    from api.v1.rooms import rooms_bp
    from api.v1.search import search_bp
    from api.v1.bookings import bookings_bp
    from api.v1.reviews import reviews_bp
    from api.v1.admin import admin_bp
    from api.v1.wishlist import wishlist_bp

    app.register_blueprint(reservations_bp, url_prefix='/api/reservations')
    app.register_blueprint(auth_bp,         url_prefix='/api/v1/auth')
    app.register_blueprint(hotels_bp,       url_prefix='/api/v1/hotels')
    app.register_blueprint(rooms_bp,        url_prefix='/api/v1/rooms')
    app.register_blueprint(search_bp,       url_prefix='/api/v1/search')
    app.register_blueprint(bookings_bp,     url_prefix='/api/v1/bookings')
    app.register_blueprint(reviews_bp,      url_prefix='/api/v1')
    app.register_blueprint(admin_bp,        url_prefix='/api/v1/admin')
    app.register_blueprint(wishlist_bp,     url_prefix='/api/v1/wishlist')

    # ------------------------------------------------------------------ #
    # Background scheduler — daily check-in reminder emails
    # Only starts when ENABLE_SCHEDULER=true (avoid multi-worker conflicts)
    # ------------------------------------------------------------------ #
    if os.environ.get('ENABLE_SCHEDULER', '').lower() == 'true':
        _start_scheduler(app)

    # ------------------------------------------------------------------ #
    # Health & diagnostics
    # ------------------------------------------------------------------ #
    @app.route('/')
    @app.route('/api/health')
    def health():
        return jsonify({"status": "ok", "message": "Hotel Reservation API"}), 200

    @app.route('/api/db-check')
    def db_check():
        try:
            from db.cassandra_client import get_session
            session = get_session()
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

    return app


def _start_scheduler(app):
    from apscheduler.schedulers.background import BackgroundScheduler

    def send_reminders():
        import datetime
        with app.app_context():
            from models.booking import Booking
            from utils.email import send_checkin_reminder
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            bookings = Booking.query.filter_by(
                check_in_date=tomorrow, status='confirmed'
            ).all()
            for b in bookings:
                try:
                    send_checkin_reminder(b, b.room, b.hotel)
                except Exception as e:
                    print(f"[scheduler] Reminder failed for {b.id}: {e}")

    scheduler = BackgroundScheduler()
    scheduler.add_job(send_reminders, 'cron', hour=9, id='checkin_reminders')
    scheduler.start()
    print("[scheduler] Check-in reminder job started.")


# Module-level app instance so Gunicorn (`gunicorn app:app`) can find it.
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
