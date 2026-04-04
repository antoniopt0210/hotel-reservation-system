import uuid
from db.postgres_client import db


class User(db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    email         = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    first_name    = db.Column(db.Text, nullable=False)
    last_name     = db.Column(db.Text, nullable=False)
    phone         = db.Column(db.Text)
    role          = db.Column(db.Text, nullable=False, default='guest')
    created_at    = db.Column(db.DateTime, server_default=db.func.now())
    updated_at    = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            'id':         self.id,
            'email':      self.email,
            'first_name': self.first_name,
            'last_name':  self.last_name,
            'phone':      self.phone,
            'role':       self.role,
        }

    ROLES = ('guest', 'hotel_admin', 'superadmin')
