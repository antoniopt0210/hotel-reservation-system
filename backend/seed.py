"""
Seed the PostgreSQL database with 3 sample hotels, rooms, and amenities.
Run from the backend/ directory:
  python seed.py
Requires DATABASE_URL to be set in your environment (or a .env file).
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from db.postgres_client import db
from models.hotel import Hotel, HotelPhoto, Amenity
from models.room import Room, RoomPhoto

app = create_app()

AMENITIES = [
    {"name": "WiFi",            "icon": "wifi"},
    {"name": "Pool",            "icon": "pool"},
    {"name": "Gym",             "icon": "gym"},
    {"name": "Parking",         "icon": "parking"},
    {"name": "Restaurant",      "icon": "restaurant"},
    {"name": "Bar",             "icon": "bar"},
    {"name": "Spa",             "icon": "spa"},
    {"name": "Pet Friendly",    "icon": "pet"},
    {"name": "Business Center", "icon": "business"},
    {"name": "Laundry",         "icon": "laundry"},
]

HOTELS = [
    {
        "name":          "The Grand Palace",
        "slug":          "the-grand-palace-new-york",
        "description":   "A iconic 5-star luxury hotel in the heart of Midtown Manhattan. Renowned for exceptional service, world-class dining, and breathtaking skyline views.",
        "address_line1": "768 Fifth Avenue",
        "city":          "New York",
        "state_province":"NY",
        "country":       "US",
        "postal_code":   "10019",
        "latitude":      40.7637,
        "longitude":     -73.9731,
        "star_rating":   5,
        "check_in_time": "15:00",
        "check_out_time":"12:00",
        "amenity_names": ["WiFi", "Restaurant", "Bar", "Spa", "Gym", "Business Center"],
        "photos": [
            {"url": "https://picsum.photos/seed/grandpalace1/800/500", "caption": "Hotel Exterior", "is_primary": True,  "sort_order": 0},
            {"url": "https://picsum.photos/seed/grandpalace2/800/500", "caption": "Lobby",          "is_primary": False, "sort_order": 1},
            {"url": "https://picsum.photos/seed/grandpalace3/800/500", "caption": "Rooftop Bar",    "is_primary": False, "sort_order": 2},
        ],
        "rooms": [
            {
                "name": "Deluxe King Room", "room_type": "King",
                "description": "Spacious room with king bed and Manhattan skyline views.",
                "max_occupancy": 2, "base_price_usd": 349.00, "total_units": 20,
                "size_sqft": 420, "bed_count": 1,
                "photos": [{"url": "https://picsum.photos/seed/gproom1/800/500", "is_primary": True, "sort_order": 0}],
            },
            {
                "name": "Executive Suite", "room_type": "Suite",
                "description": "Luxurious suite with separate living area, soaking tub, and panoramic views.",
                "max_occupancy": 3, "base_price_usd": 599.00, "total_units": 8,
                "size_sqft": 780, "bed_count": 1,
                "photos": [{"url": "https://picsum.photos/seed/gproom2/800/500", "is_primary": True, "sort_order": 0}],
            },
            {
                "name": "Standard Queen Room", "room_type": "Queen",
                "description": "Comfortable room with queen bed and city views.",
                "max_occupancy": 2, "base_price_usd": 249.00, "total_units": 30,
                "size_sqft": 320, "bed_count": 1,
                "photos": [{"url": "https://picsum.photos/seed/gproom3/800/500", "is_primary": True, "sort_order": 0}],
            },
        ],
    },
    {
        "name":          "Sunset Beach Resort",
        "slug":          "sunset-beach-resort-miami",
        "description":   "A vibrant 4-star beachfront resort on South Beach. Enjoy direct ocean access, three pools, and Miami's best nightlife steps away.",
        "address_line1": "1500 Ocean Drive",
        "city":          "Miami",
        "state_province":"FL",
        "country":       "US",
        "postal_code":   "33139",
        "latitude":      25.7823,
        "longitude":     -80.1300,
        "star_rating":   4,
        "check_in_time": "16:00",
        "check_out_time":"11:00",
        "amenity_names": ["WiFi", "Pool", "Restaurant", "Bar", "Parking", "Spa"],
        "photos": [
            {"url": "https://picsum.photos/seed/sunsetbeach1/800/500", "caption": "Beach View",    "is_primary": True,  "sort_order": 0},
            {"url": "https://picsum.photos/seed/sunsetbeach2/800/500", "caption": "Pool Area",     "is_primary": False, "sort_order": 1},
            {"url": "https://picsum.photos/seed/sunsetbeach3/800/500", "caption": "Ocean Suite",   "is_primary": False, "sort_order": 2},
        ],
        "rooms": [
            {
                "name": "Ocean View King", "room_type": "King",
                "description": "Wake up to stunning Atlantic Ocean views from your private balcony.",
                "max_occupancy": 2, "base_price_usd": 279.00, "total_units": 25,
                "size_sqft": 380, "bed_count": 1,
                "photos": [{"url": "https://picsum.photos/seed/sbroom1/800/500", "is_primary": True, "sort_order": 0}],
            },
            {
                "name": "Beach Suite", "room_type": "Suite",
                "description": "Expansive oceanfront suite with private terrace and kitchenette.",
                "max_occupancy": 4, "base_price_usd": 449.00, "total_units": 10,
                "size_sqft": 650, "bed_count": 2,
                "photos": [{"url": "https://picsum.photos/seed/sbroom2/800/500", "is_primary": True, "sort_order": 0}],
            },
            {
                "name": "Standard Double", "room_type": "Double",
                "description": "Comfortable room with two double beds, perfect for friends or families.",
                "max_occupancy": 4, "base_price_usd": 179.00, "total_units": 35,
                "size_sqft": 300, "bed_count": 2,
                "photos": [{"url": "https://picsum.photos/seed/sbroom3/800/500", "is_primary": True, "sort_order": 0}],
            },
        ],
    },
    {
        "name":          "Mountain View Lodge",
        "slug":          "mountain-view-lodge-denver",
        "description":   "A cozy 3-star lodge nestled in the Denver foothills. The perfect base for skiing, hiking, and Rocky Mountain adventures.",
        "address_line1": "2200 Mountain Road",
        "city":          "Denver",
        "state_province":"CO",
        "country":       "US",
        "postal_code":   "80202",
        "latitude":      39.7392,
        "longitude":     -104.9903,
        "star_rating":   3,
        "check_in_time": "15:00",
        "check_out_time":"11:00",
        "amenity_names": ["WiFi", "Parking", "Pet Friendly", "Laundry", "Gym"],
        "photos": [
            {"url": "https://picsum.photos/seed/mountainlodge1/800/500", "caption": "Lodge Exterior",  "is_primary": True,  "sort_order": 0},
            {"url": "https://picsum.photos/seed/mountainlodge2/800/500", "caption": "Mountain Views",  "is_primary": False, "sort_order": 1},
            {"url": "https://picsum.photos/seed/mountainlodge3/800/500", "caption": "Cozy Common Area","is_primary": False, "sort_order": 2},
        ],
        "rooms": [
            {
                "name": "Standard King", "room_type": "King",
                "description": "Rustic-chic room with king bed and mountain views.",
                "max_occupancy": 2, "base_price_usd": 149.00, "total_units": 15,
                "size_sqft": 280, "bed_count": 1,
                "photos": [{"url": "https://picsum.photos/seed/mlroom1/800/500", "is_primary": True, "sort_order": 0}],
            },
            {
                "name": "Double Room", "room_type": "Double",
                "description": "Two double beds with forest views, great for groups.",
                "max_occupancy": 4, "base_price_usd": 119.00, "total_units": 20,
                "size_sqft": 260, "bed_count": 2,
                "photos": [{"url": "https://picsum.photos/seed/mlroom2/800/500", "is_primary": True, "sort_order": 0}],
            },
            {
                "name": "Family Suite", "room_type": "Suite",
                "description": "Spacious suite with bunk beds, kitchenette, and fireplace.",
                "max_occupancy": 6, "base_price_usd": 219.00, "total_units": 8,
                "size_sqft": 500, "bed_count": 3,
                "photos": [{"url": "https://picsum.photos/seed/mlroom3/800/500", "is_primary": True, "sort_order": 0}],
            },
        ],
    },
]


def seed():
    with app.app_context():
        # Amenities
        amenity_map = {}
        for a in AMENITIES:
            existing = Amenity.query.filter_by(name=a['name']).first()
            if not existing:
                obj = Amenity(name=a['name'], icon=a['icon'])
                db.session.add(obj)
                db.session.flush()
                amenity_map[a['name']] = obj
            else:
                amenity_map[a['name']] = existing

        # Hotels
        for h in HOTELS:
            if Hotel.query.filter_by(slug=h['slug']).first():
                print(f"  Hotel '{h['slug']}' already exists — skipping.")
                continue

            hotel = Hotel(
                name=h['name'], slug=h['slug'], description=h['description'],
                address_line1=h['address_line1'], city=h['city'],
                state_province=h['state_province'], country=h['country'],
                postal_code=h['postal_code'], latitude=h['latitude'],
                longitude=h['longitude'], star_rating=h['star_rating'],
                check_in_time=h['check_in_time'], check_out_time=h['check_out_time'],
            )
            for name in h['amenity_names']:
                if name in amenity_map:
                    hotel.amenities.append(amenity_map[name])

            db.session.add(hotel)
            db.session.flush()

            for p in h['photos']:
                db.session.add(HotelPhoto(hotel_id=hotel.id, **p))

            for r in h['rooms']:
                room_photos = r.pop('photos', [])
                room = Room(hotel_id=hotel.id, **r)
                db.session.add(room)
                db.session.flush()
                for rp in room_photos:
                    db.session.add(RoomPhoto(room_id=room.id, **rp))
                r['photos'] = room_photos  # restore for idempotency

            print(f"  Seeded: {hotel.name}")

        db.session.commit()
        print("Seed complete.")


if __name__ == '__main__':
    seed()
