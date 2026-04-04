import uuid
from db.postgres_client import db


class Review(db.Model):
    __tablename__ = 'reviews'

    id         = db.Column(db.Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    hotel_id   = db.Column(db.Text, db.ForeignKey('hotels.id', ondelete='CASCADE'), nullable=False)
    booking_id = db.Column(db.Text, db.ForeignKey('bookings.id', ondelete='SET NULL'))
    user_id    = db.Column(db.Text, db.ForeignKey('users.id', ondelete='SET NULL'))
    rating     = db.Column(db.SmallInteger, nullable=False)   # 1–5
    title      = db.Column(db.Text)
    body       = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user    = db.relationship('User',    backref='reviews', lazy=True)
    booking = db.relationship('Booking', backref='review',  lazy=True, uselist=False)

    def to_dict(self):
        return {
            'id':         self.id,
            'hotel_id':   self.hotel_id,
            'booking_id': self.booking_id,
            'rating':     self.rating,
            'title':      self.title,
            'body':       self.body,
            'created_at': str(self.created_at),
            'reviewer':   (
                f"{self.user.first_name} {self.user.last_name[0]}."
                if self.user and self.user.last_name else
                (self.user.first_name if self.user else 'Guest')
            ),
        }
