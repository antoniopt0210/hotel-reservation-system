"""
Reservation model — thin data class used for serialization/validation.
In Phase 2 this pattern is expanded with SQLAlchemy models for hotels, rooms, etc.
"""
from dataclasses import dataclass, field
from typing import Optional
import datetime
import uuid


@dataclass
class Reservation:
    first_name: str
    last_name: str
    check_in_date: str
    check_out_date: str
    room_type: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    birthday: Optional[str] = None
    extra_info: Optional[str] = None
    status: str = "Booked"
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'birthday': self.birthday,
            'check_in_date': self.check_in_date,
            'check_out_date': self.check_out_date,
            'room_type': self.room_type,
            'extra_info': self.extra_info,
            'status': self.status,
            'created_at': self.created_at,
        }

    VALID_STATUSES = ('Booked', 'Checked-In', 'Checked-Out', 'Canceled')
    VALID_ROOM_TYPES = ('King bed', 'Queen bed', 'Double beds')
