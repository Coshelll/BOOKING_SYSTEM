"""
app.py — Графический интерфейс для системы бронирования (tkinter)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import logging

from backend import BookingSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BookingApp:
    """Главное окно приложения"""

    def __init__(self, root):
        self.root = root
        self.root.title("🏨 Система бронирования ресторана")
        self.root.geometry("950x650")

        self.system = BookingSystem()
        self.system.init_database()

        # Автоматически завершаем просроченные бронирования при запуске
        expired_count = self.system.auto_complete_expired_bookings()
        if expired_count:
            print(f"⏰ {expired_count} просроченных бронирований автоматически завершено")

        # Создаём вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладки
        self.users_tab = ttk.Frame(self.notebook)
        self.tables_tab = ttk.Frame(self.notebook)
        self.bookings_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.users_tab, text="👤 Пользователи")
        self.notebook.add(self.tables_tab, text="🍽️ Столики")
        self.notebook.add(self.bookings_tab, text="📋 Бронирования")

        # Заполняем вкладки
        self.setup_users_tab()
        self.setup_tables_tab()
        self.setup_bookings_tab()

        # Загружаем данные
        self.refresh_users()
        self.refresh_tables()
        self.refresh_bookings()
        self.refresh_combos()

    # ============ ВКЛАДКА "ПОЛЬЗОВАТЕЛИ" ============
    def setup_users_tab(self):
        """Настройка вкладки пользователей"""
        form_frame = ttk.LabelFrame(self.users_tab, text="➕ Добавить пользователя")
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(form_frame, text="Имя:").grid(row=0, column=0, padx=5, pady=5)
        self.user_first_name = ttk.Entry(form_frame, width=20)
        self.user_first_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Фамилия:").grid(row=0, column=2, padx=5, pady=5)
        self.user_last_name = ttk.Entry(form_frame, width=20)
        self.user_last_name.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Email:").grid(row=0, column=4, padx=5, pady=5)
        self.user_email = ttk.Entry(form_frame, width=25)
        self.user_email.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(form_frame, text="Телефон:").grid(row=0, column=6, padx=5, pady=5)
        self.user_phone = ttk.Entry(form_frame, width=15)
        self.user_phone.grid(row=0, column=7, padx=5, pady=5)

        btn_add = ttk.Button(form_frame, text="Сохранить", command=self.add_user)
        btn_add.grid(row=0, column=8, padx=10, pady=5)

        # Список пользователей
        list_frame = ttk.LabelFrame(self.users_tab, text="📋 Список пользователей")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("ID", "Имя", "Фамилия", "Email", "Телефон")
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=100 if col == "ID" else 150)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)

        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def add_user(self):
        """Добавляет пользователя"""
        first_name = self.user_first_name.get().strip()
        last_name = self.user_last_name.get().strip()
        email = self.user_email.get().strip()
        phone = self.user_phone.get().strip()

        if not first_name or not last_name or not email:
            messagebox.showerror("Ошибка", "Имя, фамилия и email обязательны!")
            return

        try:
            user_id = self.system.create_user(email, first_name, last_name, phone)
            if user_id:
                messagebox.showinfo("Успех", f"Пользователь добавлен! ID: {user_id}")
                self.user_first_name.delete(0, tk.END)
                self.user_last_name.delete(0, tk.END)
                self.user_email.delete(0, tk.END)
                self.user_phone.delete(0, tk.END)
                self.refresh_users()
                self.refresh_combos()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить пользователя")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def refresh_users(self):
        """Обновляет список пользователей"""
        for row in self.users_tree.get_children():
            self.users_tree.delete(row)

        users = self.system.get_all_users()
        for user in users:
            self.users_tree.insert("", tk.END, values=(
                user.id, user.first_name, user.last_name, user.email, user.phone
            ))

    # ============ ВКЛАДКА "СТОЛИКИ" ============
    def setup_tables_tab(self):
        """Настройка вкладки столиков"""
        form_frame = ttk.LabelFrame(self.tables_tab, text="➕ Добавить столик")
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(form_frame, text="Номер:").grid(row=0, column=0, padx=5, pady=5)
        self.table_number = ttk.Entry(form_frame, width=10)
        self.table_number.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Кол-во мест:").grid(row=0, column=2, padx=5, pady=5)
        self.table_seats = ttk.Entry(form_frame, width=10)
        self.table_seats.grid(row=0, column=3, padx=5, pady=5)

        btn_add = ttk.Button(form_frame, text="Сохранить", command=self.add_table)
        btn_add.grid(row=0, column=4, padx=10, pady=5)

        list_frame = ttk.LabelFrame(self.tables_tab, text="📋 Список столиков")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("ID", "Номер", "Мест", "Статус")
        self.tables_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.tables_tree.heading(col, text=col)
            self.tables_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tables_tree.yview)
        self.tables_tree.configure(yscrollcommand=scrollbar.set)

        self.tables_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def add_table(self):
        """Добавляет столик"""
        number_str = self.table_number.get().strip()
        seats_str = self.table_seats.get().strip()

        if not number_str:
            messagebox.showerror("Ошибка", "Номер столика обязателен!")
            return

        try:
            number = int(number_str)
            seats = int(seats_str) if seats_str else 2
            table_id = self.system.create_table(number, seats)
            if table_id:
                messagebox.showinfo("Успех", f"Столик добавлен! ID: {table_id}")
                self.table_number.delete(0, tk.END)
                self.table_seats.delete(0, tk.END)
                self.refresh_tables()
                self.refresh_combos()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить столик")
        except ValueError:
            messagebox.showerror("Ошибка", "Номер и места должны быть числами!")

    def refresh_tables(self):
        """Обновляет список столиков"""
        for row in self.tables_tree.get_children():
            self.tables_tree.delete(row)

        tables = self.system.get_all_tables()
        for table in tables:
            status_emoji = "🟢" if table.status == "available" else "🔴" if table.status == "reserved" else "🟡"
            self.tables_tree.insert("", tk.END, values=(
                table.id, table.number, table.seats, f"{status_emoji} {table.status}"
            ))

    # ============ ВКЛАДКА "БРОНИРОВАНИЯ" ============
    def setup_bookings_tab(self):
        """Настройка вкладки бронирований"""
        form_frame = ttk.LabelFrame(self.bookings_tab, text="➕ Создать бронирование")
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(form_frame, text="Пользователь:").grid(row=0, column=0, padx=5, pady=5)
        self.booking_user = ttk.Combobox(form_frame, width=25)
        self.booking_user.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Столик:").grid(row=0, column=2, padx=5, pady=5)
        self.booking_table = ttk.Combobox(form_frame, width=15)
        self.booking_table.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Дата/Время:").grid(row=1, column=0, padx=5, pady=5)
        self.booking_time = ttk.Entry(form_frame, width=20)
        self.booking_time.grid(row=1, column=1, padx=5, pady=5)
        self.booking_time.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))

        ttk.Label(form_frame, text="Длительность (часы):").grid(row=1, column=2, padx=5, pady=5)
        self.booking_duration = ttk.Entry(form_frame, width=10)
        self.booking_duration.grid(row=1, column=3, padx=5, pady=5)
        self.booking_duration.insert(0, "2")

        ttk.Label(form_frame, text="Примечания:").grid(row=1, column=4, padx=5, pady=5)
        self.booking_notes = ttk.Entry(form_frame, width=20)
        self.booking_notes.grid(row=1, column=5, padx=5, pady=5)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=6, pady=10)

        btn_check = ttk.Button(btn_frame, text="🔍 Проверить доступность", command=self.check_availability)
        btn_check.pack(side=tk.LEFT, padx=5)

        btn_create = ttk.Button(btn_frame, text="📝 Создать бронирование", command=self.create_booking)
        btn_create.pack(side=tk.LEFT, padx=5)

        # Список бронирований
        list_frame = ttk.LabelFrame(self.bookings_tab, text="📋 Список бронирований")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("ID", "Клиент", "Столик", "Время", "Статус", "Примечания")
        self.bookings_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.bookings_tree.heading(col, text=col)
            self.bookings_tree.column(col, width=100 if col == "ID" else 150)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.bookings_tree.yview)
        self.bookings_tree.configure(yscrollcommand=scrollbar.set)

        self.bookings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки управления бронированиями
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        btn_cancel = ttk.Button(action_frame, text="❌ Отменить", command=self.cancel_booking)
        btn_cancel.pack(side=tk.LEFT, padx=5)

        btn_complete = ttk.Button(action_frame, text="✅ Завершить", command=self.complete_booking)
        btn_complete.pack(side=tk.LEFT, padx=5)

        btn_auto_clean = ttk.Button(
            action_frame,
            text="🧹 Очистить просроченные",
            command=self.auto_clean_expired
        )
        btn_auto_clean.pack(side=tk.LEFT, padx=5)

    def refresh_combos(self):
        """Обновляет выпадающие списки"""
        users = self.system.get_all_users()
        self.booking_user['values'] = [f"{u.id}: {u.full_name()} ({u.email})" for u in users]

        tables = self.system.get_all_tables()
        self.booking_table['values'] = [f"{t.id}: №{t.number} ({t.seats} мест)" for t in tables]

    def get_selected_ids(self):
        """Получает выбранные ID пользователя и столика"""
        user_str = self.booking_user.get()
        table_str = self.booking_table.get()

        if not user_str or not table_str:
            messagebox.showerror("Ошибка", "Выберите пользователя и столик!")
            return None, None

        try:
            user_id = int(user_str.split(":")[0])
            table_id = int(table_str.split(":")[0])
            return user_id, table_id
        except (ValueError, IndexError):
            messagebox.showerror("Ошибка", "Некорректный выбор!")
            return None, None

    def check_availability(self):
        """Проверяет доступность столика"""
        user_id, table_id = self.get_selected_ids()
        if not user_id or not table_id:
            return

        time_str = self.booking_time.get().strip()
        duration_str = self.booking_duration.get().strip()

        try:
            booking_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            duration = int(duration_str) if duration_str else 2

            available = self.system.check_table_availability(table_id, booking_time, duration)

            if available:
                messagebox.showinfo("Доступно", "✅ Столик свободен на выбранное время!")
            else:
                messagebox.showwarning("Занято", "❌ Столик уже забронирован на это время!")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте: ГГГГ-ММ-ДД ЧЧ:ММ")

    def create_booking(self):
        """Создаёт бронирование"""
        user_id, table_id = self.get_selected_ids()
        if not user_id or not table_id:
            return

        time_str = self.booking_time.get().strip()
        duration_str = self.booking_duration.get().strip()
        notes = self.booking_notes.get().strip()

        try:
            booking_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            duration = int(duration_str) if duration_str else 2

            booking_id = self.system.create_booking(
                user_id, table_id, booking_time, duration, notes
            )

            if booking_id:
                messagebox.showinfo("Успех", f"✅ Бронирование создано! ID: {booking_id}")
                self.refresh_bookings()
                self.refresh_combos()
                self.refresh_tables()
            else:
                messagebox.showerror("Ошибка", "❌ Не удалось создать бронирование")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты!")

    def refresh_bookings(self):
        """Обновляет список бронирований"""
        for row in self.bookings_tree.get_children():
            self.bookings_tree.delete(row)

        bookings = self.system.get_booking_details()
        for b in bookings:
            # Преобразуем datetime в строку
            booking_time = b['booking_time']
            if isinstance(booking_time, datetime):
                time_str = booking_time.strftime("%Y-%m-%d %H:%M")
            elif booking_time:
                time_str = str(booking_time)[:16]
            else:
                time_str = "—"

            self.bookings_tree.insert("", tk.END, values=(
                b['booking_id'],
                b['customer_name'],
                f"№{b['table_number']}",
                time_str,
                b['status'],
                b.get('notes', '')[:20]
            ))

    def get_selected_booking_id(self):
        """Получает ID выбранного бронирования"""
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите бронирование!")
            return None
        values = self.bookings_tree.item(selected[0])['values']
        return values[0]

    def cancel_booking(self):
        """Отменяет бронирование"""
        booking_id = self.get_selected_booking_id()
        if not booking_id:
            return

        if messagebox.askyesno("Подтверждение", f"Отменить бронирование #{booking_id}?"):
            if self.system.cancel_booking(booking_id):
                messagebox.showinfo("Успех", "✅ Бронирование отменено")
                self.refresh_bookings()
                self.refresh_tables()
            else:
                messagebox.showerror("Ошибка", "❌ Не удалось отменить бронирование")

    def complete_booking(self):
        """Завершает бронирование (только если время уже наступило)"""
        booking_id = self.get_selected_booking_id()
        if not booking_id:
            return

        if messagebox.askyesno("Подтверждение", f"Завершить бронирование #{booking_id}?"):
            if self.system.complete_booking(booking_id):
                messagebox.showinfo("Успех", "✅ Бронирование завершено")
                self.refresh_bookings()
                self.refresh_tables()
            else:
                messagebox.showerror(
                    "Ошибка",
                    "❌ Не удалось завершить бронирование.\n"
                    "Возможно, время ещё не наступило — используйте 'Отменить'."
                )

    def auto_clean_expired(self):
        """Вручную запускает очистку просроченных бронирований"""
        count = self.system.auto_complete_expired_bookings()
        self.refresh_bookings()
        self.refresh_tables()
        messagebox.showinfo("Авто-очистка", f"🧹 Завершено {count} просроченных бронирований")


def main():
    root = tk.Tk()
    app = BookingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()