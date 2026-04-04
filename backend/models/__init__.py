# Import all models here so SQLAlchemy's db.create_all() picks them up.
from models.user import User          # noqa: F401
from models.hotel import Hotel, HotelPhoto, Amenity, hotel_amenities  # noqa: F401
from models.room import Room, RoomPhoto      # noqa: F401
from models.booking import Booking          # noqa: F401
from models.review import Review            # noqa: F401
from models.wishlist import WishlistItem    # noqa: F401
