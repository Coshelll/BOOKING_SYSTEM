"""
Модель Booking — описывает бронирование столика
Связывает пользователя (User) и столик (Table)
"""

from datetime import datetime
from typing import Optional


class Booking:
    """Модель бронирования"""

    def __init__(
        self,
        id: int = None,
        user_id: int = None,
        table_id: int = None,
        booking_time: datetime = None,
        duration_hours: int = 2,
        status: str = "active",  # active, completed, cancelled
        notes: str = "",
        created_at: datetime = None
    ):
        self.id = id
        self.user_id = user_id
        self.table_id = table_id
        self.booking_time = booking_time or datetime.now()
        self.duration_hours = duration_hours
        self.status = status
        self.notes = notes
        self.created_at = created_at or datetime.now()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id"),
            table_id=data.get("table_id"),
            booking_time=data.get("booking_time"),
            duration_hours=data.get("duration_hours", 2),
            status=data.get("status", "active"),
            notes=data.get("notes", ""),
            created_at=data.get("created_at")
        )

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "table_id": self.table_id,
            "booking_time": self.booking_time,
            "duration_hours": self.duration_hours,
            "status": self.status,
            "notes": self.notes,
        }

    def __str__(self):
        return (
            f"Booking(id={self.id}, user_id={self.user_id}, "
            f"table_id={self.table_id}, time={self.booking_time}, "
            f"status={self.status})"
        )

    def __repr__(self):
        return self.__str__()


# SQL для создания таблицы bookings
BOOKING_TABLE_SCHEMA = """
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    table_id INTEGER NOT NULL REFERENCES tables(id) ON DELETE CASCADE,
    booking_time TIMESTAMP NOT NULL,
    duration_hours INTEGER DEFAULT 2,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
"""