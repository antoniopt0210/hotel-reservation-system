"""
Search endpoints — autocomplete and full-text-like search.
"""
from flask import Blueprint, request, jsonify
from db.postgres_client import db
from models.hotel import Hotel

search_bp = Blueprint('search', __name__)


@search_bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    """
    Return matching city names and hotel names for typeahead.
    Query param: ?q=<text>
    """
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify({'suggestions': []})

    pattern = f'%{q}%'

    # Distinct cities
    city_rows = (
        db.session.query(Hotel.city)
        .filter(Hotel.is_active == True, Hotel.city.ilike(pattern))
        .distinct()
        .limit(5)
        .all()
    )
    cities = [{'type': 'city', 'value': r.city} for r in city_rows]

    # Hotel names
    hotel_rows = (
        Hotel.query
        .filter(Hotel.is_active == True, Hotel.name.ilike(pattern))
        .limit(5)
        .all()
    )
    hotels = [{'type': 'hotel', 'value': h.name, 'slug': h.slug, 'city': h.city} for h in hotel_rows]

    return jsonify({'suggestions': cities + hotels})
