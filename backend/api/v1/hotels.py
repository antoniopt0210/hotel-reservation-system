import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db.postgres_client import db
from models.hotel import Hotel, HotelPhoto, Amenity, hotel_amenities
from models.room import Room
from utils.auth_helpers import admin_required

hotels_bp = Blueprint('hotels', __name__)


# ---------------------------------------------------------------------------
# Public endpoints
# ---------------------------------------------------------------------------

@hotels_bp.route('', methods=['GET'])
def list_hotels():
    city       = request.args.get('city', '').strip()
    stars      = request.args.get('stars', '')
    amenity_ids = request.args.get('amenities', '')
    min_price  = request.args.get('min_price', type=float)
    max_price  = request.args.get('max_price', type=float)
    guests     = request.args.get('guests', type=int)
    sort       = request.args.get('sort', 'rating_desc')
    page       = max(int(request.args.get('page', 1)), 1)
    limit      = min(int(request.args.get('limit', 20)), 50)

    query = Hotel.query.filter(Hotel.is_active == True)

    if city:
        query = query.filter(Hotel.city.ilike(f'%{city}%'))

    if stars:
        star_list = [int(s) for s in stars.split(',') if s.strip().isdigit()]
        if star_list:
            query = query.filter(Hotel.star_rating.in_(star_list))

    if amenity_ids:
        for aid in (int(a) for a in amenity_ids.split(',') if a.strip().isdigit()):
            query = query.filter(
                Hotel.id.in_(
                    db.session.query(hotel_amenities.c.hotel_id)
                    .filter(hotel_amenities.c.amenity_id == aid)
                )
            )

    # Price / occupancy filters: restrict to hotels that have at least one
    # matching room — but keep the query on Hotel level for pagination.
    if min_price is not None or max_price is not None or guests:
        room_q = db.session.query(Room.hotel_id).filter(Room.is_active == True)
        if min_price is not None:
            room_q = room_q.filter(Room.base_price_usd >= min_price)
        if max_price is not None:
            room_q = room_q.filter(Room.base_price_usd <= max_price)
        if guests:
            room_q = room_q.filter(Room.max_occupancy >= guests)
        query = query.filter(Hotel.id.in_(room_q))

    if sort == 'price_asc':
        price_sub = (
            db.session.query(db.func.min(Room.base_price_usd).label('min_price'), Room.hotel_id)
            .filter(Room.is_active == True)
            .group_by(Room.hotel_id)
            .subquery()
        )
        query = query.outerjoin(price_sub, Hotel.id == price_sub.c.hotel_id) \
                     .order_by(price_sub.c.min_price.asc().nullslast())
    elif sort == 'price_desc':
        price_sub = (
            db.session.query(db.func.min(Room.base_price_usd).label('min_price'), Room.hotel_id)
            .filter(Room.is_active == True)
            .group_by(Room.hotel_id)
            .subquery()
        )
        query = query.outerjoin(price_sub, Hotel.id == price_sub.c.hotel_id) \
                     .order_by(price_sub.c.min_price.desc().nullslast())
    else:
        # Default: sort by star_rating descending
        query = query.order_by(Hotel.star_rating.desc().nullslast())

    paginated = query.paginate(page=page, per_page=limit, error_out=False)

    return jsonify({
        "hotels":      [h.to_dict() for h in paginated.items],
        "total":       paginated.total,
        "page":        page,
        "pages":       paginated.pages,
        "limit":       limit,
    }), 200


@hotels_bp.route('/<slug>', methods=['GET'])
def get_hotel(slug):
    hotel = Hotel.query.filter_by(slug=slug, is_active=True).first()
    if not hotel:
        return jsonify({"error": "Hotel not found"}), 404
    return jsonify({"hotel": hotel.to_dict(include_rooms=True)}), 200


@hotels_bp.route('/<hotel_id>/rooms', methods=['GET'])
def get_hotel_rooms(hotel_id):
    check_in  = request.args.get('check_in')
    check_out = request.args.get('check_out')
    guests    = request.args.get('guests', type=int)

    hotel = Hotel.query.filter(
        (Hotel.id == hotel_id) | (Hotel.slug == hotel_id),
        Hotel.is_active == True
    ).first()
    if not hotel:
        return jsonify({"error": "Hotel not found"}), 404

    rooms = Room.query.filter_by(hotel_id=hotel.id, is_active=True)
    if guests:
        rooms = rooms.filter(Room.max_occupancy >= guests)
    rooms = rooms.all()

    # Availability check via Cassandra (Phase 2 basic version)
    if check_in and check_out:
        rooms = _filter_available_rooms(rooms, check_in, check_out)

    return jsonify({"rooms": [r.to_dict() for r in rooms]}), 200


def _filter_available_rooms(rooms, check_in: str, check_out: str) -> list:
    """
    Filter rooms by Cassandra availability. A room is available if every
    night in the range has available_units > 0 (or no record, meaning fully open).
    """
    try:
        from db.cassandra_client import get_session, KEYSPACE
        session = get_session()

        ci = datetime.date.fromisoformat(check_in)
        co = datetime.date.fromisoformat(check_out)
        nights = (co - ci).days
        if nights <= 0:
            return rooms

        stay_dates = [ci + datetime.timedelta(days=i) for i in range(nights)]

        available = []
        for room in rooms:
            blocked = False
            for d in stay_dates:
                ym = d.strftime('%Y-%m')
                row = session.execute(
                    f"SELECT available_units FROM {KEYSPACE}.room_availability "
                    f"WHERE room_id = %s AND year_month = %s AND stay_date = %s",
                    (room.id, ym, d.isoformat())
                ).one()
                # A missing row means full availability; explicit 0 means sold out
                if row is not None and row.available_units <= 0:
                    blocked = True
                    break
            if not blocked:
                available.append(room)
        return available
    except Exception:
        # If Cassandra is unreachable, fall back to returning all rooms
        return rooms


# ---------------------------------------------------------------------------
# Admin endpoints
# ---------------------------------------------------------------------------

@hotels_bp.route('/admin', methods=['POST'])
@admin_required
def create_hotel():
    data = request.get_json() or {}
    required = ('name', 'slug', 'city', 'country')
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if Hotel.query.filter_by(slug=data['slug']).first():
        return jsonify({"error": "Slug already in use"}), 409

    hotel = Hotel(
        owner_user_id  = get_jwt_identity(),
        name           = data['name'],
        slug           = data['slug'],
        description    = data.get('description'),
        address_line1  = data.get('address_line1'),
        city           = data['city'],
        state_province = data.get('state_province'),
        country        = data['country'],
        postal_code    = data.get('postal_code'),
        latitude       = data.get('latitude'),
        longitude      = data.get('longitude'),
        star_rating    = data.get('star_rating'),
        check_in_time  = data.get('check_in_time', '15:00'),
        check_out_time = data.get('check_out_time', '11:00'),
    )
    db.session.add(hotel)

    # Attach amenities
    for aid in data.get('amenity_ids', []):
        amenity = Amenity.query.get(aid)
        if amenity:
            hotel.amenities.append(amenity)

    db.session.commit()
    return jsonify({"hotel": hotel.to_dict()}), 201


@hotels_bp.route('/admin/<hotel_id>', methods=['PUT'])
@admin_required
def update_hotel(hotel_id):
    hotel = Hotel.query.get(hotel_id)
    if not hotel:
        return jsonify({"error": "Hotel not found"}), 404

    data = request.get_json() or {}
    updatable = ('name', 'description', 'address_line1', 'city', 'state_province',
                 'country', 'postal_code', 'latitude', 'longitude',
                 'star_rating', 'check_in_time', 'check_out_time', 'is_active')
    for field in updatable:
        if field in data:
            setattr(hotel, field, data[field])

    if 'amenity_ids' in data:
        hotel.amenities = [a for a in Amenity.query.filter(
            Amenity.id.in_(data['amenity_ids'])
        ).all()]

    db.session.commit()
    return jsonify({"hotel": hotel.to_dict()}), 200


@hotels_bp.route('/admin/<hotel_id>/rooms', methods=['POST'])
@admin_required
def create_room(hotel_id):
    hotel = Hotel.query.get(hotel_id)
    if not hotel:
        return jsonify({"error": "Hotel not found"}), 404

    data = request.get_json() or {}
    required = ('name', 'room_type', 'base_price_usd')
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    room = Room(
        hotel_id       = hotel_id,
        name           = data['name'],
        room_type      = data['room_type'],
        description    = data.get('description'),
        max_occupancy  = data.get('max_occupancy', 2),
        base_price_usd = data['base_price_usd'],
        total_units    = data.get('total_units', 1),
        size_sqft      = data.get('size_sqft'),
        bed_count      = data.get('bed_count'),
    )
    db.session.add(room)
    db.session.commit()
    return jsonify({"room": room.to_dict()}), 201


@hotels_bp.route('/admin/rooms/<room_id>', methods=['PUT'])
@admin_required
def update_room(room_id):
    room = Room.query.get(room_id)
    if not room:
        return jsonify({"error": "Room not found"}), 404

    data = request.get_json() or {}
    updatable = ('name', 'room_type', 'description', 'max_occupancy',
                 'base_price_usd', 'total_units', 'size_sqft', 'bed_count', 'is_active')
    for field in updatable:
        if field in data:
            setattr(room, field, data[field])

    db.session.commit()
    return jsonify({"room": room.to_dict()}), 200


@hotels_bp.route('/amenities', methods=['GET'])
def list_amenities():
    return jsonify({"amenities": [a.to_dict() for a in Amenity.query.all()]}), 200
