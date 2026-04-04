import uuid
from db.postgres_client import db


class Room(db.Model):
    __tablename__ = 'rooms'

    id              = db.Column(db.Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    hotel_id        = db.Column(db.Text, db.ForeignKey('hotels.id', ondelete='CASCADE'), nullable=False)
    name            = db.Column(db.Text, nullable=False)
    room_type       = db.Column(db.Text, nullable=False)   # King | Queen | Double | Suite
    description     = db.Column(db.Text)
    max_occupancy   = db.Column(db.SmallInteger, nullable=False, default=2)
    base_price_usd  = db.Column(db.Numeric(10, 2), nullable=False)
    total_units     = db.Column(db.SmallInteger, nullable=False, default=1)
    size_sqft       = db.Column(db.Integer)
    bed_count       = db.Column(db.SmallInteger)
    is_active       = db.Column(db.Boolean, default=True)

    photos = db.relationship('RoomPhoto', backref='room', lazy=True,
                             cascade='all, delete-orphan', order_by='RoomPhoto.sort_order')

    def to_dict(self):
        return {
            'id':             self.id,
            'hotel_id':       self.hotel_id,
            'name':           self.name,
            'room_type':      self.room_type,
            'description':    self.description,
            'max_occupancy':  self.max_occupancy,
            'base_price_usd': float(self.base_price_usd),
            'total_units':    self.total_units,
            'size_sqft':      self.size_sqft,
            'bed_count':      self.bed_count,
            'photos':         [p.to_dict() for p in self.photos],
        }


class RoomPhoto(db.Model):
    __tablename__ = 'room_photos'

    id         = db.Column(db.Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    room_id    = db.Column(db.Text, db.ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False)
    url        = db.Column(db.Text, nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.SmallInteger, default=0)

    def to_dict(self):
        return {'id': self.id, 'url': self.url, 'is_primary': self.is_primary}
