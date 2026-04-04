"""
Seed the PostgreSQL database with hotels across all major US cities.
Run from the backend/ directory:
  python seed.py
Requires DATABASE_URL to be set in your environment (or a .env file).
"""
import os
import random
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from db.postgres_client import db
from models.hotel import Hotel, HotelPhoto, Amenity
from models.room import Room, RoomPhoto

app = create_app()

random.seed(42)  # reproducible results

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
    {"name": "Room Service",    "icon": "room_service"},
    {"name": "Airport Shuttle", "icon": "shuttle"},
    {"name": "Concierge",       "icon": "concierge"},
    {"name": "Rooftop Terrace", "icon": "rooftop"},
    {"name": "EV Charging",     "icon": "ev"},
]

# ── US Cities ────────────────────────────────────────────────────────────────
CITIES = [
    {"city": "New York",       "state": "NY", "lat": 40.7128,  "lng": -74.0060},
    {"city": "Los Angeles",    "state": "CA", "lat": 34.0522,  "lng": -118.2437},
    {"city": "Chicago",        "state": "IL", "lat": 41.8781,  "lng": -87.6298},
    {"city": "Houston",        "state": "TX", "lat": 29.7604,  "lng": -95.3698},
    {"city": "Phoenix",        "state": "AZ", "lat": 33.4484,  "lng": -112.0740},
    {"city": "Philadelphia",   "state": "PA", "lat": 39.9526,  "lng": -75.1652},
    {"city": "San Antonio",    "state": "TX", "lat": 29.4241,  "lng": -98.4936},
    {"city": "San Diego",      "state": "CA", "lat": 32.7157,  "lng": -117.1611},
    {"city": "Dallas",         "state": "TX", "lat": 32.7767,  "lng": -96.7970},
    {"city": "San Jose",       "state": "CA", "lat": 37.3382,  "lng": -121.8863},
    {"city": "Austin",         "state": "TX", "lat": 30.2672,  "lng": -97.7431},
    {"city": "Jacksonville",   "state": "FL", "lat": 30.3322,  "lng": -81.6557},
    {"city": "Fort Worth",     "state": "TX", "lat": 32.7555,  "lng": -97.3308},
    {"city": "Columbus",       "state": "OH", "lat": 39.9612,  "lng": -82.9988},
    {"city": "Indianapolis",   "state": "IN", "lat": 39.7684,  "lng": -86.1581},
    {"city": "Charlotte",      "state": "NC", "lat": 35.2271,  "lng": -80.8431},
    {"city": "San Francisco",  "state": "CA", "lat": 37.7749,  "lng": -122.4194},
    {"city": "Seattle",        "state": "WA", "lat": 47.6062,  "lng": -122.3321},
    {"city": "Denver",         "state": "CO", "lat": 39.7392,  "lng": -104.9903},
    {"city": "Nashville",      "state": "TN", "lat": 36.1627,  "lng": -86.7816},
    {"city": "Oklahoma City",  "state": "OK", "lat": 35.4676,  "lng": -97.5164},
    {"city": "Washington",     "state": "DC", "lat": 38.9072,  "lng": -77.0369},
    {"city": "El Paso",        "state": "TX", "lat": 31.7619,  "lng": -106.4850},
    {"city": "Boston",         "state": "MA", "lat": 42.3601,  "lng": -71.0589},
    {"city": "Portland",       "state": "OR", "lat": 45.5152,  "lng": -122.6784},
    {"city": "Las Vegas",      "state": "NV", "lat": 36.1699,  "lng": -115.1398},
    {"city": "Memphis",        "state": "TN", "lat": 35.1495,  "lng": -90.0490},
    {"city": "Louisville",     "state": "KY", "lat": 38.2527,  "lng": -85.7585},
    {"city": "Baltimore",      "state": "MD", "lat": 39.2904,  "lng": -76.6122},
    {"city": "Milwaukee",      "state": "WI", "lat": 43.0389,  "lng": -87.9065},
    {"city": "Albuquerque",    "state": "NM", "lat": 35.0844,  "lng": -106.6504},
    {"city": "Tucson",         "state": "AZ", "lat": 32.2226,  "lng": -110.9747},
    {"city": "Fresno",         "state": "CA", "lat": 36.7378,  "lng": -119.7871},
    {"city": "Sacramento",     "state": "CA", "lat": 38.5816,  "lng": -121.4944},
    {"city": "Mesa",           "state": "AZ", "lat": 33.4152,  "lng": -111.8315},
    {"city": "Kansas City",    "state": "MO", "lat": 39.0997,  "lng": -94.5786},
    {"city": "Atlanta",        "state": "GA", "lat": 33.7490,  "lng": -84.3880},
    {"city": "Omaha",          "state": "NE", "lat": 41.2565,  "lng": -95.9345},
    {"city": "Colorado Springs", "state": "CO", "lat": 38.8339, "lng": -104.8214},
    {"city": "Raleigh",        "state": "NC", "lat": 35.7796,  "lng": -78.6382},
    {"city": "Long Beach",     "state": "CA", "lat": 33.7701,  "lng": -118.1937},
    {"city": "Virginia Beach", "state": "VA", "lat": 36.8529,  "lng": -75.9780},
    {"city": "Miami",          "state": "FL", "lat": 25.7617,  "lng": -80.1918},
    {"city": "Oakland",        "state": "CA", "lat": 37.8044,  "lng": -122.2712},
    {"city": "Minneapolis",    "state": "MN", "lat": 44.9778,  "lng": -93.2650},
    {"city": "Tampa",          "state": "FL", "lat": 27.9506,  "lng": -82.4572},
    {"city": "Tulsa",          "state": "OK", "lat": 36.1540,  "lng": -95.9928},
    {"city": "Arlington",      "state": "TX", "lat": 32.7357,  "lng": -97.1081},
    {"city": "New Orleans",    "state": "LA", "lat": 29.9511,  "lng": -90.0715},
    {"city": "Wichita",        "state": "KS", "lat": 37.6872,  "lng": -97.3301},
    {"city": "Cleveland",      "state": "OH", "lat": 41.4993,  "lng": -81.6944},
    {"city": "Bakersfield",    "state": "CA", "lat": 35.3733,  "lng": -119.0187},
    {"city": "Aurora",         "state": "CO", "lat": 39.7294,  "lng": -104.8319},
    {"city": "Anaheim",        "state": "CA", "lat": 33.8366,  "lng": -117.9143},
    {"city": "Honolulu",       "state": "HI", "lat": 21.3069,  "lng": -157.8583},
    {"city": "Santa Ana",      "state": "CA", "lat": 33.7455,  "lng": -117.8677},
    {"city": "Riverside",      "state": "CA", "lat": 33.9806,  "lng": -117.3755},
    {"city": "Corpus Christi", "state": "TX", "lat": 27.8006,  "lng": -97.3964},
    {"city": "Pittsburgh",     "state": "PA", "lat": 40.4406,  "lng": -79.9959},
    {"city": "Lexington",      "state": "KY", "lat": 38.0406,  "lng": -84.5037},
    {"city": "Anchorage",      "state": "AK", "lat": 61.2181,  "lng": -149.9003},
    {"city": "Stockton",       "state": "CA", "lat": 37.9577,  "lng": -121.2908},
    {"city": "St. Louis",      "state": "MO", "lat": 38.6270,  "lng": -90.1994},
    {"city": "Cincinnati",     "state": "OH", "lat": 39.1031,  "lng": -84.5120},
    {"city": "St. Paul",       "state": "MN", "lat": 44.9537,  "lng": -93.0900},
    {"city": "Newark",         "state": "NJ", "lat": 40.7357,  "lng": -74.1724},
    {"city": "Greensboro",     "state": "NC", "lat": 36.0726,  "lng": -79.7920},
    {"city": "Buffalo",        "state": "NY", "lat": 42.8864,  "lng": -78.8784},
    {"city": "Plano",          "state": "TX", "lat": 33.0198,  "lng": -96.6989},
    {"city": "Lincoln",        "state": "NE", "lat": 40.8136,  "lng": -96.7026},
    {"city": "Orlando",        "state": "FL", "lat": 28.5383,  "lng": -81.3792},
    {"city": "Irvine",         "state": "CA", "lat": 33.6846,  "lng": -117.8265},
    {"city": "Norfolk",        "state": "VA", "lat": 36.8508,  "lng": -76.2859},
    {"city": "Durham",         "state": "NC", "lat": 35.9940,  "lng": -78.8986},
    {"city": "Madison",        "state": "WI", "lat": 43.0731,  "lng": -89.4012},
    {"city": "Boise",          "state": "ID", "lat": 43.6150,  "lng": -116.2023},
    {"city": "Richmond",       "state": "VA", "lat": 37.5407,  "lng": -77.4360},
    {"city": "Des Moines",     "state": "IA", "lat": 41.5868,  "lng": -93.6250},
    {"city": "Salt Lake City", "state": "UT", "lat": 40.7608,  "lng": -111.8910},
    {"city": "Rochester",      "state": "NY", "lat": 43.1566,  "lng": -77.6088},
    {"city": "Spokane",        "state": "WA", "lat": 47.6588,  "lng": -117.4260},
    {"city": "Birmingham",     "state": "AL", "lat": 33.5207,  "lng": -86.8025},
    {"city": "Charleston",     "state": "SC", "lat": 32.7765,  "lng": -79.9311},
    {"city": "Savannah",       "state": "GA", "lat": 32.0809,  "lng": -81.0912},
    {"city": "Providence",     "state": "RI", "lat": 41.8240,  "lng": -71.4128},
    {"city": "Little Rock",    "state": "AR", "lat": 34.7465,  "lng": -92.2896},
    {"city": "Jackson",        "state": "MS", "lat": 32.2988,  "lng": -90.1848},
    {"city": "Sioux Falls",    "state": "SD", "lat": 43.5460,  "lng": -96.7313},
    {"city": "Fargo",          "state": "ND", "lat": 46.8772,  "lng": -96.7898},
    {"city": "Billings",       "state": "MT", "lat": 45.7833,  "lng": -108.5007},
    {"city": "Burlington",     "state": "VT", "lat": 44.4759,  "lng": -73.2121},
    {"city": "Portland",       "state": "ME", "lat": 43.6591,  "lng": -70.2568},
    {"city": "Wilmington",     "state": "DE", "lat": 39.7391,  "lng": -75.5398},
    {"city": "Manchester",     "state": "NH", "lat": 42.9956,  "lng": -71.4548},
    {"city": "Cheyenne",       "state": "WY", "lat": 41.1400,  "lng": -104.8202},
    {"city": "Hartford",       "state": "CT", "lat": 41.7658,  "lng": -72.6734},
    {"city": "Baton Rouge",    "state": "LA", "lat": 30.4515,  "lng": -91.1871},
    {"city": "Scottsdale",     "state": "AZ", "lat": 33.4942,  "lng": -111.9261},
    {"city": "Naperville",     "state": "IL", "lat": 41.7508,  "lng": -88.1535},
]

# ── Hotel name templates ─────────────────────────────────────────────────────
HOTEL_TEMPLATES = {
    5: [
        {"prefix": "The Ritz",              "desc": "Unparalleled luxury with white-glove service, Michelin-star dining, and opulent suites designed for the most discerning travelers."},
        {"prefix": "Grand Meridian",        "desc": "An iconic five-star landmark offering world-class amenities, rooftop infinity pool, and award-winning culinary experiences."},
        {"prefix": "The Peninsula",         "desc": "Timeless elegance meets modern sophistication. Lavish rooms, a rejuvenating spa, and breathtaking city views from every angle."},
    ],
    4: [
        {"prefix": "Hilton Garden",         "desc": "Upscale comfort in a prime location. Enjoy spacious rooms, an on-site restaurant, indoor pool, and a fully equipped fitness center."},
        {"prefix": "Courtyard",             "desc": "Modern rooms with premium bedding, a stylish lobby bistro, and flexible meeting spaces. Ideal for business and leisure."},
        {"prefix": "Hyatt Place",           "desc": "Contemporary design with gallery-style rooms, complimentary breakfast, a rooftop bar, and seamless connectivity throughout."},
        {"prefix": "Embassy Suites",        "desc": "All-suite hotel with separate living areas, made-to-order breakfast, and an evening reception with complimentary drinks."},
    ],
    3: [
        {"prefix": "Comfort Inn",           "desc": "Clean, reliable, and affordable. Free hot breakfast, indoor pool, and friendly staff to make your stay feel like home."},
        {"prefix": "Holiday Inn Express",   "desc": "Smart, simple, and well-located. Enjoy the Express Start breakfast bar, crisp linens, and modern amenities at a great price."},
        {"prefix": "Hampton Inn",           "desc": "Warm hospitality and modern comfort. Complimentary breakfast, free WiFi, and spotless rooms with ergonomic workspaces."},
        {"prefix": "Best Western Plus",     "desc": "Great value with thoughtful extras: fitness center, seasonal pool, business center, and pet-friendly rooms available."},
        {"prefix": "La Quinta Inn",         "desc": "Bright, welcoming rooms with pillow-top mattresses. Free breakfast, pet-friendly policy, and pool access included."},
    ],
    2: [
        {"prefix": "Motel 6",              "desc": "Budget-friendly stays with everything you need: clean rooms, free WiFi, and convenient highway access for road trippers."},
        {"prefix": "Super 8",              "desc": "No-frills comfort at an unbeatable price. Continental breakfast, free parking, and a great night's sleep guaranteed."},
        {"prefix": "Red Roof Inn",         "desc": "Affordable and pet-friendly. Simple rooms with free WiFi, coffee in the lobby, and easy access to local attractions."},
    ],
}

AMENITIES_BY_STARS = {
    5: ["WiFi", "Pool", "Gym", "Restaurant", "Bar", "Spa", "Business Center", "Concierge", "Room Service", "Rooftop Terrace"],
    4: ["WiFi", "Pool", "Gym", "Restaurant", "Bar", "Business Center", "Parking", "Room Service"],
    3: ["WiFi", "Pool", "Gym", "Parking", "Laundry", "Pet Friendly"],
    2: ["WiFi", "Parking", "Laundry", "Pet Friendly"],
}

ROOM_TEMPLATES = {
    5: [
        {"name": "Premier King Suite",   "room_type": "Suite", "max_occupancy": 2, "base_min": 350, "base_max": 650, "units": 8,  "sqft": 700, "beds": 1},
        {"name": "Deluxe King Room",     "room_type": "King",  "max_occupancy": 2, "base_min": 250, "base_max": 450, "units": 20, "sqft": 450, "beds": 1},
        {"name": "Grand Queen Room",     "room_type": "Queen", "max_occupancy": 2, "base_min": 200, "base_max": 380, "units": 25, "sqft": 380, "beds": 1},
        {"name": "Presidential Suite",   "room_type": "Suite", "max_occupancy": 4, "base_min": 800, "base_max": 1500,"units": 3,  "sqft": 1200,"beds": 2},
    ],
    4: [
        {"name": "Executive King Room",  "room_type": "King",  "max_occupancy": 2, "base_min": 180, "base_max": 320, "units": 25, "sqft": 380, "beds": 1},
        {"name": "Superior Queen Room",  "room_type": "Queen", "max_occupancy": 2, "base_min": 140, "base_max": 260, "units": 30, "sqft": 320, "beds": 1},
        {"name": "Junior Suite",         "room_type": "Suite", "max_occupancy": 3, "base_min": 250, "base_max": 420, "units": 10, "sqft": 550, "beds": 1},
        {"name": "Family Double Room",   "room_type": "Double","max_occupancy": 4, "base_min": 160, "base_max": 280, "units": 20, "sqft": 350, "beds": 2},
    ],
    3: [
        {"name": "Standard King Room",   "room_type": "King",  "max_occupancy": 2, "base_min": 100, "base_max": 200, "units": 20, "sqft": 280, "beds": 1},
        {"name": "Standard Queen Room",  "room_type": "Queen", "max_occupancy": 2, "base_min": 80,  "base_max": 160, "units": 30, "sqft": 250, "beds": 1},
        {"name": "Double Room",          "room_type": "Double","max_occupancy": 4, "base_min": 90,  "base_max": 170, "units": 25, "sqft": 270, "beds": 2},
    ],
    2: [
        {"name": "Standard Room",        "room_type": "Queen", "max_occupancy": 2, "base_min": 55,  "base_max": 100, "units": 30, "sqft": 220, "beds": 1},
        {"name": "Double Room",          "room_type": "Double","max_occupancy": 4, "base_min": 65,  "base_max": 120, "units": 25, "sqft": 240, "beds": 2},
    ],
}

PHOTO_SEEDS = [
    "luxhotel", "cityview", "beachhotel", "lobbyarea", "poolside",
    "rooftop", "bedroom", "suite", "bathroom", "restaurant",
    "skyline", "resort", "garden", "terrace", "lounge",
    "fountain", "hallway", "modern", "cozy", "elegant",
]


def _slug(name, city, state):
    return f"{name}-{city}".lower().replace(' ', '-').replace('.', '').replace("'", '') + f"-{state.lower()}"


def _make_hotel_photos(hotel_name, city, idx):
    seed_base = f"{hotel_name}{city}{idx}".replace(' ', '').lower()
    captions = ["Hotel Exterior", "Lobby & Reception", "Room Interior"]
    return [
        {
            "url": f"https://picsum.photos/seed/{seed_base}{i}/800/500",
            "caption": captions[i] if i < len(captions) else f"Photo {i+1}",
            "is_primary": i == 0,
            "sort_order": i,
        }
        for i in range(random.randint(2, 4))
    ]


def _make_room_photo(hotel_name, room_name):
    seed = f"{hotel_name}{room_name}".replace(' ', '').lower()
    return {"url": f"https://picsum.photos/seed/{seed}/800/500", "is_primary": True, "sort_order": 0}


def generate_hotels():
    """Generate 1-3 random hotels for each US city."""
    hotels = []
    used_slugs = set()

    for city_data in CITIES:
        city  = city_data["city"]
        state = city_data["state"]
        lat   = city_data["lat"]
        lng   = city_data["lng"]

        num_hotels = random.randint(1, 3)

        # Pick star ratings — ensure variety
        star_options = [5, 4, 4, 3, 3, 3, 2]
        stars_chosen = random.sample(star_options, min(num_hotels, len(star_options)))

        for i in range(num_hotels):
            stars = stars_chosen[i]
            templates = HOTEL_TEMPLATES[stars]
            template = random.choice(templates)

            name = f"{template['prefix']} {city}"
            slug = _slug(template['prefix'], city, state)

            # Avoid duplicate slugs
            if slug in used_slugs:
                slug += f"-{i+1}"
            used_slugs.add(slug)

            # Small random offset for lat/lng so hotels aren't stacked
            h_lat = round(lat + random.uniform(-0.02, 0.02), 6)
            h_lng = round(lng + random.uniform(-0.02, 0.02), 6)

            # Pick amenities
            amenity_pool = AMENITIES_BY_STARS[stars]
            num_amenities = random.randint(max(3, len(amenity_pool) - 3), len(amenity_pool))
            hotel_amenities = random.sample(amenity_pool, num_amenities)

            # Pick rooms (2-4 room types)
            room_pool = ROOM_TEMPLATES[stars]
            num_rooms = random.randint(2, min(4, len(room_pool)))
            room_picks = random.sample(room_pool, num_rooms)

            rooms = []
            for rt in room_picks:
                price = round(random.uniform(rt["base_min"], rt["base_max"]), 2)
                rooms.append({
                    "name": rt["name"],
                    "room_type": rt["room_type"],
                    "description": f"{rt['name']} with modern amenities and city views.",
                    "max_occupancy": rt["max_occupancy"],
                    "base_price_usd": price,
                    "total_units": rt["units"],
                    "size_sqft": rt["sqft"],
                    "bed_count": rt["beds"],
                    "photos": [_make_room_photo(name, rt["name"])],
                })

            hotels.append({
                "name": name,
                "slug": slug,
                "description": template["desc"],
                "address_line1": f"{random.randint(100, 9999)} {random.choice(['Main St', 'Broadway', 'Market St', 'First Ave', 'Park Ave', 'Ocean Blvd', 'Elm St', 'Maple Dr', 'Center Blvd', 'Commerce St'])}",
                "city": city,
                "state_province": state,
                "country": "US",
                "postal_code": f"{random.randint(10000, 99999)}",
                "latitude": h_lat,
                "longitude": h_lng,
                "star_rating": stars,
                "check_in_time": random.choice(["14:00", "15:00", "16:00"]),
                "check_out_time": random.choice(["10:00", "11:00", "12:00"]),
                "amenity_names": hotel_amenities,
                "photos": _make_hotel_photos(name, city, i),
                "rooms": rooms,
            })

    return hotels


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

        # Generate and seed hotels
        hotels_data = generate_hotels()
        count = 0

        for h in hotels_data:
            if Hotel.query.filter_by(slug=h['slug']).first():
                print(f"  Already exists — skipping: {h['name']}")
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

            count += 1
            print(f"  [{count}] Seeded: {hotel.name} ({h['city']}, {h['state_province']}) — {h['star_rating']}★")

        db.session.commit()
        print(f"\nSeed complete. {count} new hotels added ({len(hotels_data)} total generated).")


if __name__ == '__main__':
    seed()
