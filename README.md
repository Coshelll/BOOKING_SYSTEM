# 🏨 Система бронирования ресторана

![Превью проекта](images/preview.jpg)

---

## 📌 Описание

Мини-система бронирования столиков в ресторане с использованием **PostgreSQL**, **Python** и **tkinter**.

---

## 🚀 Возможности

- Управление пользователями (CRUD)
- Управление столиками (CRUD)
- Управление бронированиями (CRUD)
- Проверка доступности столиков
- Графический интерфейс (tkinter)

---

## 🛠️ Установка

### 1. Клонировать проект

```bash
git clone <your-repo-url>
cd booking_system
```

### 2. Создать виртуальное окружение

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Настроить .env

Создай `.env` по образцу `.env.example`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=booking
DB_USER=postgres
DB_PASSWORD=12345
```

### 5. Создать базу данных

```sql
CREATE DATABASE booking;
```

---

## 🚀 Запуск

### CLI-версия

```bash
python main.py
```

### GUI-версия

```bash
python app.py
```

---

## 📁 Структура проекта

```text
booking_system/
├── .env.example
├── requirements.txt
├── postgres_driver.py
├── backend.py
├── main.py              # CLI-интерфейс
├── app.py               # GUI-интерфейс
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── table.py
│   └── booking.py
├── images/
│   └── preview.jpg
└── README.md
```

---

## ✅ Тестовые данные

При первом запуске автоматически создаются:

- 2 пользователя
- 9 столиков (1–9)

---

## 📄 Лицензия

MIT
