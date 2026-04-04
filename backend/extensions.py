"""
Shared extension singletons.
Import these into blueprints — never import from app.py directly to avoid circular imports.
"""
from flask_cors import CORS

cors = CORS()
