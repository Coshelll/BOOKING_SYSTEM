"""
main.py — CLI-интерфейс для системы бронирования
"""

import logging
from datetime import datetime
from backend import BookingSystem

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def print_users(system):
    users = system.get_all_users()
    if not users:
        print("📭 Нет пользователей")
        return
    print("\n👥 ПОЛЬЗОВАТЕЛИ:")
    print("-" * 60)
    for u in users:
        print(f"  {u.id}. {u.full_name()} ({u.email}) — {u.phone}")


def print_tables(system):
    tables = system.get_all_tables()
    if not tables:
        print("📭 Нет столиков")
        return
    print("\n🍽️ СТОЛИКИ:")
    print("-" * 60)
    for t in tables:
        status_emoji = "🟢" if t.status == "available" else "🔴" if t.status == "reserved" else "🟡"
        print(f"  {t.number}. {t.seats} мест — {status_emoji} {t.status}")


def print_bookings(system):
    bookings = system.get_booking_details()
    if not bookings:
        print("📭 Нет бронирований")
        return
    print("\n📋 БРОНИРОВАНИЯ:")
    print("-" * 80)
    print(f"{'ID':<5} {'Клиент':<20} {'Столик':<10} {'Время':<20} {'Статус':<12}")
    print("-" * 80)
    for b in bookings:
        time_str = b['booking_time'][:16] if b['booking_time'] else "—"
        print(f"{b['booking_id']:<5} {b['customer_name']:<20} "
              f"№{b['table_number']:<8} {time_str:<20} {b['status']:<12}")


def main():
    system = BookingSystem()
    system.init_database()

    # Тестовые данные (если нет пользователей)
    users = system.get_all_users()
    if not users:
        print("📌 Создаём тестовых пользователей...")
        system.create_user("alice@example.com", "Алиса", "Иванова", "+7-900-111-22-33")
        system.create_user("bob@example.com", "Боб", "Смирнов", "+7-900-222-33-44")

    # Тестовые столики
    tables = system.get_all_tables()
    if not tables:
        print("📌 Создаём тестовые столики...")
        for i in range(1, 10):
            seats = 2 if i % 3 != 0 else (4 if i % 3 == 1 else 6)
            system.create_table(i, seats)

    while True:
        print("\n" + "=" * 60)
        print("🏨 СИСТЕМА БРОНИРОВАНИЯ РЕСТОРАНА")
        print("=" * 60)
        print("1. 👤 Показать пользователей")
        print("2. 🍽️ Показать столики")
        print("3. 📋 Показать бронирования")
        print("4. ➕ Создать бронирование")
        print("5. ❌ Отменить бронирование")
        print("6. ✅ Завершить бронирование")
        print("0. 🚪 Выход")
        print("-" * 60)

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            print_users(system)

        elif choice == "2":
            print_tables(system)

        elif choice == "3":
            print_bookings(system)

        elif choice == "4":
            try:
                user_id = int(input("ID пользователя: "))
                table_id = int(input("ID столика: "))
                time_str = input("Время (ГГГГ-ММ-ДД ЧЧ:ММ): ")
                booking_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                duration = int(input("Длительность (часы, по умолчанию 2): ") or 2)
                notes = input("Примечания: ")

                booking_id = system.create_booking(
                    user_id, table_id, booking_time, duration, notes
                )
                if booking_id:
                    print(f"✅ Бронирование создано! ID: {booking_id}")
            except ValueError as e:
                print(f"❌ Ошибка ввода: {e}")

        elif choice == "5":
            try:
                booking_id = int(input("ID бронирования для отмены: "))
                if system.cancel_booking(booking_id):
                    print("✅ Бронирование отменено")
                else:
                    print("❌ Не удалось отменить бронирование")
            except ValueError:
                print("❌ Введите корректный ID")

        elif choice == "6":
            try:
                booking_id = int(input("ID бронирования для завершения: "))
                if system.complete_booking(booking_id):
                    print("✅ Бронирование завершено")
                else:
                    print("❌ Не удалось завершить бронирование")
            except ValueError:
                print("❌ Введите корректный ID")

        elif choice == "0":
            print("👋 До свидания!")
            break

        else:
            print("❌ Неверный выбор!")

        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Программа остановлена")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")