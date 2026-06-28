"""
backend.py — Основная логика системы бронирования
Содержит функции для работы с пользователями, столиками и бронированиями
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from postgres_driver import PostgresDB
from models import User, Table, Booking
from models.user import USER_TABLE_SCHEMA
from models.table import TABLE_TABLE_SCHEMA
from models.booking import BOOKING_TABLE_SCHEMA

logger = logging.getLogger(__name__)


class BookingSystem:
    """Основной класс системы бронирования"""

    def __init__(self):
        self.db = PostgresDB()

    def init_database(self):
        """Создаёт таблицы, если они не существуют"""
        with self.db as conn:
            conn.create_table("users", USER_TABLE_SCHEMA)
            conn.create_table("tables", TABLE_TABLE_SCHEMA)
            conn.create_table("bookings", BOOKING_TABLE_SCHEMA)

        logger.info("✅ База данных инициализирована")

    # ============ РАБОТА С ПОЛЬЗОВАТЕЛЯМИ ============
    def create_user(self, email: str, first_name: str,
                    last_name: str, phone: str = "") -> Optional[int]:
        """Создаёт нового пользователя"""
        user = User(email=email, first_name=first_name,
                    last_name=last_name, phone=phone)
        with self.db as conn:
            user_id = conn.insert_record("users", user.to_dict())
            if user_id:
                logger.info(f"👤 Создан пользователь: {email}")
            return user_id

    def get_user(self, user_id: int) -> Optional[User]:
        """Получает пользователя по ID"""
        with self.db as conn:
            result = conn.select_records(
                "users",
                where_clause="id = %s",
                params=(user_id,)
            )
            if result:
                return User.from_dict(result[0])
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получает пользователя по email"""
        with self.db as conn:
            result = conn.select_records(
                "users",
                where_clause="email = %s",
                params=(email,)
            )
            if result:
                return User.from_dict(result[0])
            return None

    def get_all_users(self) -> List[User]:
        """Получает всех пользователей"""
        with self.db as conn:
            results = conn.select_records("users", order_by="id")
            return [User.from_dict(row) for row in results]

    def update_user(self, user_id: int, data: Dict[str, Any]) -> bool:
        """Обновляет данные пользователя"""
        with self.db as conn:
            updated = conn.update_records(
                "users",
                data=data,
                where_clause="id = %s",
                params=(user_id,)
            )
            return updated > 0

    def delete_user(self, user_id: int) -> bool:
        """Удаляет пользователя"""
        with self.db as conn:
            deleted = conn.delete_records(
                "users",
                where_clause="id = %s",
                params=(user_id,)
            )
            return deleted > 0

    # ============ РАБОТА СО СТОЛИКАМИ ============
    def create_table(self, number: int, seats: int = 2) -> Optional[int]:
        """Создаёт новый столик"""
        table = Table(number=number, seats=seats)
        with self.db as conn:
            table_id = conn.insert_record("tables", table.to_dict())
            if table_id:
                logger.info(f"🍽️ Создан столик №{number}")
            return table_id

    def get_table(self, table_id: int) -> Optional[Table]:
        """Получает столик по ID"""
        with self.db as conn:
            result = conn.select_records(
                "tables",
                where_clause="id = %s",
                params=(table_id,)
            )
            if result:
                return Table.from_dict(result[0])
            return None

    def get_all_tables(self) -> List[Table]:
        """Получает все столики"""
        with self.db as conn:
            results = conn.select_records("tables", order_by="number")
            return [Table.from_dict(row) for row in results]

    def update_table(self, table_id: int, data: Dict[str, Any]) -> bool:
        """Обновляет данные столика"""
        with self.db as conn:
            updated = conn.update_records(
                "tables",
                data=data,
                where_clause="id = %s",
                params=(table_id,)
            )
            return updated > 0

    def delete_table(self, table_id: int) -> bool:
        """Удаляет столик"""
        with self.db as conn:
            deleted = conn.delete_records(
                "tables",
                where_clause="id = %s",
                params=(table_id,)
            )
            return deleted > 0

    def update_table_status(self, table_id: int, status: str) -> bool:
        """Обновляет статус столика"""
        with self.db as conn:
            updated = conn.update_records(
                "tables",
                data={"status": status},
                where_clause="id = %s",
                params=(table_id,)
            )
            return updated > 0

    def get_available_tables(self) -> List[Table]:
        """Получает все свободные столики"""
        with self.db as conn:
            results = conn.select_records(
                "tables",
                where_clause="status = 'available'",
                order_by="seats"
            )
            return [Table.from_dict(row) for row in results]

    # ============ РАБОТА С БРОНИРОВАНИЯМИ ============
    def create_booking(
        self,
        user_id: int,
        table_id: int,
        booking_time: datetime,
        duration_hours: int = 2,
        notes: str = ""
    ) -> Optional[int]:
        """
        Создаёт бронирование с проверкой доступности столика
        """
        # Проверяем, что столик существует и свободен
        table = self.get_table(table_id)
        if not table:
            logger.error(f"❌ Столик с ID {table_id} не найден")
            return None

        if table.status != "available":
            logger.error(f"❌ Столик №{table.number} уже занят")
            return None

        # Проверяем, не занят ли столик на это время
        if not self.check_table_availability(table_id, booking_time, duration_hours):
            logger.error("❌ Столик уже забронирован на это время")
            return None

        # Создаём бронирование
        booking = Booking(
            user_id=user_id,
            table_id=table_id,
            booking_time=booking_time,
            duration_hours=duration_hours,
            notes=notes
        )

        with self.db as conn:
            # Меняем статус столика на reserved
            conn.update_records(
                "tables",
                data={"status": "reserved"},
                where_clause="id = %s",
                params=(table_id,)
            )

            booking_id = conn.insert_record("bookings", booking.to_dict())

            if booking_id:
                logger.info(
                    f"✅ Бронирование создано: стол №{table.number}, "
                    f"пользователь ID={user_id}, время={booking_time}"
                )
            return booking_id

    def check_table_availability(
        self,
        table_id: int,
        booking_time: datetime,
        duration_hours: int = 2
    ) -> bool:
        """
        Проверяет, свободен ли столик на указанное время.
        Возвращает True, если столик свободен.
        """
        with self.db as conn:
            conflicts = conn.select_records(
                "bookings",
                where_clause="""
                    table_id = %s
                    AND status = 'active'
                    AND booking_time <= %s
                    AND booking_time + (duration_hours || ' hours')::interval > %s
                """,
                params=(table_id, booking_time, booking_time)
            )
            return len(conflicts) == 0

    def get_booking(self, booking_id: int) -> Optional[Booking]:
        """Получает бронирование по ID"""
        with self.db as conn:
            result = conn.select_records(
                "bookings",
                where_clause="id = %s",
                params=(booking_id,)
            )
            if result:
                return Booking.from_dict(result[0])
            return None

    def get_all_bookings(self) -> List[Booking]:
        """Получает все бронирования"""
        with self.db as conn:
            results = conn.select_records("bookings", order_by="booking_time DESC")
            return [Booking.from_dict(row) for row in results]

    def get_user_bookings(self, user_id: int) -> List[Booking]:
        """Получает все бронирования пользователя"""
        with self.db as conn:
            results = conn.select_records(
                "bookings",
                where_clause="user_id = %s",
                params=(user_id,),
                order_by="booking_time DESC"
            )
            return [Booking.from_dict(row) for row in results]

    def update_booking(self, booking_id: int, data: Dict[str, Any]) -> bool:
        """Обновляет данные бронирования"""
        with self.db as conn:
            updated = conn.update_records(
                "bookings",
                data=data,
                where_clause="id = %s",
                params=(booking_id,)
            )
            return updated > 0

    def delete_booking(self, booking_id: int) -> bool:
        """Удаляет бронирование (только для администратора)"""
        with self.db as conn:
            deleted = conn.delete_records(
                "bookings",
                where_clause="id = %s",
                params=(booking_id,)
            )
            return deleted > 0

    def cancel_booking(self, booking_id: int) -> bool:
        """Отменяет бронирование и освобождает столик"""
        booking = self.get_booking(booking_id)
        if not booking:
            logger.error(f"❌ Бронирование с ID {booking_id} не найдено")
            return False

        if booking.status == "cancelled":
            logger.warning(f"⚠️ Бронирование уже отменено")
            return False

        with self.db as conn:
            # Отменяем бронирование
            conn.update_records(
                "bookings",
                data={"status": "cancelled"},
                where_clause="id = %s",
                params=(booking_id,)
            )

            # Освобождаем столик
            conn.update_records(
                "tables",
                data={"status": "available"},
                where_clause="id = %s",
                params=(booking.table_id,)
            )

            logger.info(f"✅ Бронирование {booking_id} отменено")
            return True

    def complete_booking(self, booking_id: int) -> bool:
        """
        Завершает бронирование, если его время уже наступило.
        Если время бронирования ещё не наступило — предлагает отменить.
        """
        booking = self.get_booking(booking_id)
        if not booking:
            logger.error(f"❌ Бронирование с ID {booking_id} не найдено")
            return False

        if booking.status == "cancelled":
            logger.warning(f"⚠️ Бронирование уже отменено")
            return False

        if booking.status == "completed":
            logger.warning(f"⚠️ Бронирование уже завершено")
            return False

        # Проверяем, наступило ли время бронирования
        now = datetime.now()
        if booking.booking_time > now:
            # Время ещё не наступило — это отмена, а не завершение
            logger.warning(
                f"⚠️ Бронирование #{booking_id} ещё не началось "
                f"(начало в {booking.booking_time}). Используйте отмену."
            )
            return False

        with self.db as conn:
            # Завершаем бронирование
            conn.update_records(
                "bookings",
                data={"status": "completed"},
                where_clause="id = %s",
                params=(booking_id,)
            )

            # Освобождаем столик
            conn.update_records(
                "tables",
                data={"status": "available"},
                where_clause="id = %s",
                params=(booking.table_id,)
            )

            logger.info(f"✅ Бронирование {booking_id} завершено")
            return True

    # ============ АВТОМАТИЧЕСКОЕ ЗАВЕРШЕНИЕ ============
    def auto_complete_expired_bookings(self) -> int:
        """
        Автоматически завершает все активные бронирования,
        у которых время окончания (booking_time + duration_hours) прошло.
        Возвращает количество завершённых бронирований.
        """
        with self.db as conn:
            # Находим просроченные активные бронирования
            expired = conn.execute_query("""
                SELECT id, table_id
                FROM bookings
                WHERE status = 'active'
                  AND booking_time + (duration_hours || ' hours')::interval < NOW()
            """)

            if not expired:
                return 0

            # Завершаем каждое бронирование
            for booking in expired:
                booking_id = booking['id']
                table_id = booking['table_id']

                # Меняем статус бронирования
                conn.update_records(
                    "bookings",
                    data={"status": "completed"},
                    where_clause="id = %s",
                    params=(booking_id,)
                )

                # Освобождаем столик
                conn.update_records(
                    "tables",
                    data={"status": "available"},
                    where_clause="id = %s",
                    params=(table_id,)
                )

                logger.info(f"⏰ Автоматически завершено бронирование #{booking_id}, столик #{table_id} освобождён")

            return len(expired)

    # ============ ДОПОЛНИТЕЛЬНЫЕ ЗАПРОСЫ ============
    def get_booking_details(self) -> List[Dict[str, Any]]:
        """
        JOIN-запрос: детальная информация о бронированиях
        """
        with self.db as conn:
            result = conn.execute_query("""
                SELECT
                    b.id AS booking_id,
                    u.first_name || ' ' || u.last_name AS customer_name,
                    u.email AS customer_email,
                    t.number AS table_number,
                    t.seats AS table_seats,
                    b.booking_time,
                    b.duration_hours,
                    b.status,
                    b.notes
                FROM bookings b
                JOIN users u ON b.user_id = u.id
                JOIN tables t ON b.table_id = t.id
                ORDER BY b.booking_time DESC
            """)
            return result

    def get_available_tables_by_time(
        self,
        booking_time: datetime,
        seats: int = 0
    ) -> List[Table]:
        """
        Получает столики, доступные на указанное время
        """
        with self.db as conn:
            query = """
                SELECT t.*
                FROM tables t
                WHERE t.status = 'available'
                  AND t.seats >= %s
                  AND NOT EXISTS (
                      SELECT 1
                      FROM bookings b
                      WHERE b.table_id = t.id
                        AND b.status = 'active'
                        AND b.booking_time <= %s
                        AND b.booking_time + (b.duration_hours || ' hours')::interval > %s
                  )
                ORDER BY t.seats
            """
            results = conn.execute_query(query, (seats, booking_time, booking_time))
            return [Table.from_dict(row) for row in results]