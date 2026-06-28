"""
Модель Table — описывает столик в ресторане
"""

from datetime import datetime


class Table:
    """Модель столика"""

    def __init__(
        self,
        id: int = None,
        number: int = 0,
        seats: int = 2,
        status: str = "available",  # available, reserved, occupied
        created_at: datetime = None
    ):
        self.id = id
        self.number = number
        self.seats = seats
        self.status = status
        self.created_at = created_at or datetime.now()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id"),
            number=data.get("number", 0),
            seats=data.get("seats", 2),
            status=data.get("status", "available"),
            created_at=data.get("created_at")
        )

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "seats": self.seats,
            "status": self.status,
        }

    def is_available(self) -> bool:
        return self.status == "available"

    def __str__(self):
        return f"Table(id={self.id}, number={self.number}, seats={self.seats}, status={self.status})"

    def __repr__(self):
        return self.__str__()


# SQL для создания таблицы tables
TABLE_TABLE_SCHEMA = """
    id SERIAL PRIMARY KEY,
    number INTEGER UNIQUE NOT NULL,
    seats INTEGER NOT NULL CHECK (seats > 0),
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'reserved', 'occupied')),
    created_at TIMESTAMP DEFAULT NOW()
"""