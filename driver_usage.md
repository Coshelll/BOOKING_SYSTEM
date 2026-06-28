# 📘 Инструкция по использованию драйвера PostgreSQL

## 📌 Описание

`postgres_driver.py` — это универсальный драйвер для работы с PostgreSQL, который можно переиспользовать в любых Python-проектах. Он предоставляет удобные методы для CRUD-операций, работы с транзакциями и выполнения произвольных SQL-запросов.

---

## 🔧 Установка зависимостей

```bash
pip install psycopg2-binary python-dotenv

⚙️ Настройка окружения
Создай файл .env в корне проекта:

env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
Либо используй DATABASE_URL для облачных баз:

env
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require

🚀 Импорт и создание экземпляра
python
from postgres_driver import PostgresDB

db = PostgresDB()

📖 Использование
1. Контекстный менеджер (рекомендуемый способ)
Автоматически открывает и закрывает соединение:

python
with db:
    # Все операции внутри блока with
    users = db.select_records("users", limit=10)
    for user in users:
        print(user)

2. Ручное управление соединением
python
db.connect()
try:
    users = db.select_records("users")
finally:
    db.close()

📚 Доступные методы
➕ Вставка данных
python
# Вставка одной записи
user_id = db.insert_record("users", {
    "name": "Иван Петров",
    "email": "ivan@example.com",
    "age": 30
})

# Массовая вставка
users_data = [
    {"name": "Анна", "email": "anna@example.com"},
    {"name": "Сергей", "email": "sergey@example.com"}
]
db.insert_many_records("users", users_data)

📖 Чтение данных
python
# Все записи
users = db.select_records("users")

# С условием
users = db.select_records(
    "users",
    where_clause="age > %s",
    params=(18,),
    order_by="name ASC",
    limit=10
)

# Только определённые колонки
names = db.select_records("users", columns=["id", "name"])
✏️ Обновление данных
python
# Обновление записей по условию
updated = db.update_records(
    "users",
    data={"age": 31},
    where_clause="id = %s",
    params=(user_id,)
)

🗑️ Удаление данных
python
deleted = db.delete_records(
    "users",
    where_clause="id = %s",
    params=(user_id,)
)

📊 Подсчёт записей
python
total = db.count_records("users")
active = db.count_records("users", where_clause="is_active = true")

🔍 Проверка существования таблицы
python
if db.table_exists("users"):
    print("Таблица users существует")
⚡ Произвольный SQL-запрос
python
result = db.execute_raw_sql(
    "SELECT * FROM users WHERE email LIKE %s",
    ("%@gmail.com",)
)

### 🧹 Автоматическое завершение просроченных бронирований

```python
# Автоматически завершает все активные бронирования,
# у которых время окончания (booking_time + duration_hours) прошло
expired_count = system.auto_complete_expired_bookings()
print(f"Завершено {expired_count} просроченных бронирований")

Как это работает:

Проверяет все active бронирования

Если booking_time + duration_hours < NOW() → меняет статус на completed

Освобождает столики (меняет статус на available)

Возвращает количество завершённых бронирований

Где использовать:

При запуске приложения (авто-очистка)

По кнопке в интерфейсе ("🧹 Очистить просроченные")

В фоновом задании (например, раз в минуту/час)

text

---

## 📄 Полный раздел «Бронирования» в `driver_usage.md`

Если хочешь заменить целиком, вот полный блок:

```markdown
## 📚 Доступные методы

### 🍽️ Бронирования

```python
# Создать бронирование
booking_id = system.create_booking(
    user_id=1,
    table_id=2,
    booking_time=datetime(2026, 6, 28, 19, 0),
    duration_hours=2,
    notes="У окна"
)

# Проверить доступность столика
is_free = system.check_table_availability(
    table_id=2,
    booking_time=datetime(2026, 6, 28, 19, 0),
    duration_hours=2
)

# Получить все бронирования
bookings = system.get_all_bookings()

# Получить бронирования пользователя
bookings = system.get_user_bookings(user_id=1)

# Отменить бронирование (освобождает столик)
system.cancel_booking(booking_id=5)

# Завершить бронирование (только если время уже наступило)
system.complete_booking(booking_id=5)

# 🧹 АВТОМАТИЧЕСКОЕ ЗАВЕРШЕНИЕ ПРОСРОЧЕННЫХ
# Завершает все активные бронирования, у которых время прошло
expired_count = system.auto_complete_expired_bookings()
print(f"Завершено {expired_count} просроченных бронирований")

# JOIN-запрос: детальная информация о бронированиях
details = system.get_booking_details()
for booking in details:
    print(f"{booking['customer_name']} — стол №{booking['table_number']}")
    
📌 Как работает auto_complete_expired_bookings()
Шаг	Что происходит
1	Находит все active бронирования, где booking_time + duration_hours < NOW()
2	Меняет их статус на completed
3	Освобождает столики (меняет статус на available)
4	Возвращает количество обработанных бронирований
Пример использования:

python
# При запуске приложения
expired = system.auto_complete_expired_bookings()
if expired:
    print(f"🧹 Автоматически завершено {expired} бронирований")