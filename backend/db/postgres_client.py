"""
PostgreSQL client — added in Phase 2.
Uses SQLAlchemy for ORM and connection pooling.

Required environment variables (Phase 2):
  DATABASE_URL — full Postgres connection string, e.g.:
    postgresql://user:password@host:5432/dbname
"""
import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    """Bind SQLAlchemy to the Flask app. Call from the app factory."""
    database_url = os.environ.get('DATABASE_URL', '')

    # Supabase / Heroku provide 'postgres://' — SQLAlchemy requires 'postgresql://'
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
