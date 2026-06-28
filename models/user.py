"""
Модель User — описывает пользователя системы бронирования
"""

from datetime import datetime


class User:
    """Модель пользователя"""

    def __init__(
        self,
        id: int = None,
        email: str = "",
        first_name: str = "",
        last_name: str = "",
        phone: str = "",
        created_at: datetime = None
    ):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.created_at = created_at or datetime.now()

    @classmethod
    def from_dict(cls, data: dict):
        """Создаёт объект User из словаря (результата SELECT)"""
        return cls(
            id=data.get("id"),
            email=data.get("email", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            phone=data.get("phone", ""),
            created_at=data.get("created_at")
        )

    def to_dict(self) -> dict:
        """Преобразует объект в словарь для вставки в БД"""
        return {
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
        }

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"User(id={self.id}, email={self.email}, name={self.full_name()})"

    def __repr__(self):
        return self.__str__()


# SQL для создания таблицы users
USER_TABLE_SCHEMA = """
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
"""