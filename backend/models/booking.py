import uuid
from db.postgres_client import db


class Booking(db.Model):
    __tablename__ = 'bookings'

    id                  = db.Column(db.Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id             = db.Column(db.Text, db.ForeignKey('users.id'))
    room_id             = db.Column(db.Text, db.ForeignKey('rooms.id'))
    hotel_id            = db.Column(db.Text, db.ForeignKey('hotels.id'))
    check_in_date       = db.Column(db.Date, nullable=False)
    check_out_date      = db.Column(db.Date, nullable=False)
    guest_first_name    = db.Column(db.Text, nullable=False)
    guest_last_name     = db.Column(db.Text, nullable=False)
    guest_email         = db.Column(db.Text, nullable=False)
    num_guests          = db.Column(db.SmallInteger, default=1)
    special_requests    = db.Column(db.Text)
    total_price_usd     = db.Column(db.Numeric(10, 2), nullable=False)
    stripe_payment_id   = db.Column(db.Text)
    status              = db.Column(db.Text, default='confirmed')
    created_at          = db.Column(db.DateTime, server_default=db.func.now())
    cancelled_at        = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)

    room  = db.relationship('Room',  backref='bookings', lazy=True)
    hotel = db.relationship('Hotel', backref='bookings', lazy=True)
    user  = db.relationship('User',  backref='bookings', lazy=True)

    STATUSES = ('confirmed', 'checked_in', 'checked_out', 'cancelled', 'refunded')

    def to_dict(self):
        return {
            'id':                 self.id,
            'room_id':            self.room_id,
            'hotel_id':           self.hotel_id,
            'check_in_date':      str(self.check_in_date),
            'check_out_date':     str(self.check_out_date),
            'guest_first_name':   self.guest_first_name,
            'guest_last_name':    self.guest_last_name,
            'guest_email':        self.guest_email,
            'num_guests':         self.num_guests,
            'special_requests':   self.special_requests,
            'total_price_usd':    float(self.total_price_usd),
            'stripe_payment_id':  self.stripe_payment_id,
            'status':             self.status,
            'created_at':         str(self.created_at),
            'hotel_name':         self.hotel.name if self.hotel else None,
            'room_name':          self.room.name  if self.room  else None,
            'hotel_slug':         self.hotel.slug if self.hotel else None,
        }
