import uuid
from db.postgres_client import db


class WishlistItem(db.Model):
    __tablename__ = 'wishlist_items'

    id       = db.Column(db.Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id  = db.Column(db.Text, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    hotel_id = db.Column(db.Text, db.ForeignKey('hotels.id', ondelete='CASCADE'), nullable=False)
    added_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (db.UniqueConstraint('user_id', 'hotel_id', name='uq_user_hotel'),)

    hotel = db.relationship('Hotel', lazy=True)
