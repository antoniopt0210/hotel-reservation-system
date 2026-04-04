import uuid
from db.postgres_client import db


# Many-to-many join table
hotel_amenities = db.Table(
    'hotel_amenities',
    db.Column('hotel_id',   db.Text, db.ForeignKey('hotels.id',    ondelete='CASCADE'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenities.id'), primary_key=True),
)


class Amenity(db.Model):
    __tablename__ = 'amenities'

    id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    icon = db.Column(db.Text)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'icon': self.icon}


class Hotel(db.Model):
    __tablename__ = 'hotels'

    id              = db.Column(db.Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_user_id   = db.Column(db.Text, db.ForeignKey('users.id'))
    name            = db.Column(db.Text, nullable=False)
    slug            = db.Column(db.Text, unique=True, nullable=False)
    description     = db.Column(db.Text)
    address_line1   = db.Column(db.Text)
    city            = db.Column(db.Text, nullable=False)
    state_province  = db.Column(db.Text)
    country         = db.Column(db.Text, nullable=False)
    postal_code     = db.Column(db.Text)
    latitude        = db.Column(db.Numeric(9, 6))
    longitude       = db.Column(db.Numeric(9, 6))
    star_rating     = db.Column(db.SmallInteger)
    check_in_time   = db.Column(db.Text, default='15:00')
    check_out_time  = db.Column(db.Text, default='11:00')
    is_active       = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime, server_default=db.func.now())

    photos    = db.relationship('HotelPhoto', backref='hotel', lazy=True,
                                cascade='all, delete-orphan', order_by='HotelPhoto.sort_order')
    amenities = db.relationship('Amenity', secondary=hotel_amenities, lazy=True)
    rooms     = db.relationship('Room', backref='hotel', lazy=True,
                                cascade='all, delete-orphan')
    reviews   = db.relationship('Review', backref='hotel', lazy=True,
                                cascade='all, delete-orphan')

    def to_dict(self, include_rooms=False):
        active_rooms = [r for r in self.rooms if r.is_active]
        min_price = min((r.base_price_usd for r in active_rooms), default=None)

        ratings = [rv.rating for rv in self.reviews]
        avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else None

        data = {
            'id':             self.id,
            'name':           self.name,
            'slug':           self.slug,
            'description':    self.description,
            'address_line1':  self.address_line1,
            'city':           self.city,
            'state_province': self.state_province,
            'country':        self.country,
            'postal_code':    self.postal_code,
            'latitude':       float(self.latitude)  if self.latitude  else None,
            'longitude':      float(self.longitude) if self.longitude else None,
            'star_rating':    self.star_rating,
            'check_in_time':  self.check_in_time,
            'check_out_time': self.check_out_time,
            'min_price':      float(min_price) if min_price else None,
            'photos':         [p.to_dict() for p in self.photos],
            'amenities':      [a.to_dict() for a in self.amenities],
            'avg_rating':     avg_rating,
            'review_count':   len(ratings),
        }
        if include_rooms:
            data['rooms'] = [r.to_dict() for r in active_rooms]
        return data


class HotelPhoto(db.Model):
    __tablename__ = 'hotel_photos'

    id         = db.Column(db.Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    hotel_id   = db.Column(db.Text, db.ForeignKey('hotels.id', ondelete='CASCADE'), nullable=False)
    url        = db.Column(db.Text, nullable=False)
    caption    = db.Column(db.Text)
    is_primary = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.SmallInteger, default=0)

    def to_dict(self):
        return {
            'id':         self.id,
            'url':        self.url,
            'caption':    self.caption,
            'is_primary': self.is_primary,
        }
