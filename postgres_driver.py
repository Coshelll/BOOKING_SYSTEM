"""
postgres_driver.py — Драйвер для работы с PostgreSQL.
Содержит класс PostgresDB с поддержкой автосоздания таблиц по моделям.
"""

import os
import logging
import psycopg2
from psycopg2 import sql, extras
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Union

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgresDB:
    """Драйвер для подключения и работы с PostgreSQL."""

    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "postgres")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "")
        self.sslmode = os.getenv("DB_SSLMODE", "prefer")
        self.database_url = os.getenv("DATABASE_URL")
        self.connection = None
        self.cursor = None

    def _get_connection_params(self) -> dict:
        if self.database_url:
            return {"dsn": self.database_url}
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": self.password,
            "sslmode": self.sslmode,
        }

    def connect(self):
        try:
            params = self._get_connection_params()
            if "dsn" in params:
                self.connection = psycopg2.connect(params["dsn"])
            else:
                self.connection = psycopg2.connect(**params)
            self.connection.autocommit = False
            logger.info("✅ Успешное подключение к PostgreSQL")
            return self.connection
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
            raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info("🔒 Соединение с PostgreSQL закрыто")

    def __enter__(self):
        self.connect()
        self.cursor = self.connection.cursor(cursor_factory=extras.RealDictCursor)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.connection.rollback()
            logger.error(f"❌ Ошибка в транзакции: {exc_value}")
        else:
            self.connection.commit()
            logger.info("✅ Транзакция закоммичена")
        self.close()
        return False

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        try:
            self.cursor.execute(query, params)
            if self.cursor.description is not None:
                rows = self.cursor.fetchall()
                return [dict(row) for row in rows]
            return []
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения запроса: {e}")
            raise

    def execute_write(self, query: str, params: tuple = ()) -> int:
        try:
            self.cursor.execute(query, params)
            return self.cursor.rowcount
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения запроса: {e}")
            raise

    def insert_record(self, table_name: str, data: Dict[str, Any]) -> int:
        columns = data.keys()
        placeholders = [f"%({key})s" for key in columns]
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING id").format(
            sql.Identifier(table_name),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(sql.SQL(p) for p in placeholders)
        )
        self.cursor.execute(query, data)
        result = self.cursor.fetchone()
        return result.get("id") if result else None

    def insert_many_records(self, table_name: str, data_list: List[Dict[str, Any]]) -> int:
        if not data_list:
            return 0
        columns = list(data_list[0].keys())
        values = [[row[col] for col in columns] for row in data_list]
        query = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
            sql.Identifier(table_name),
            sql.SQL(", ").join(map(sql.Identifier, columns))
        )
        extras.execute_values(self.cursor, query.as_string(self.connection), values)
        return len(data_list)

    def select_records(
        self,
        table_name: str,
        columns: Union[str, List[str]] = "*",
        where_clause: str = "",
        params: tuple = (),
        order_by: str = "",
        limit: int = 0,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        if isinstance(columns, list):
            columns = ", ".join(columns)
        query = f"SELECT {columns} FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit > 0:
            query += f" LIMIT {limit}"
        if offset > 0:
            query += f" OFFSET {offset}"
        return self.execute_query(query, params)

    def update_records(self, table_name: str, data: Dict[str, Any],
                       where_clause: str, params: tuple = ()) -> int:
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        all_params = tuple(data.values()) + params
        return self.execute_write(query, all_params)

    def delete_records(self, table_name: str, where_clause: str,
                       params: tuple = ()) -> int:
        query = f"DELETE FROM {table_name} WHERE {where_clause}"
        return self.execute_write(query, params)

    def count_records(self, table_name: str, where_clause: str = "",
                      params: tuple = ()) -> int:
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        result = self.execute_query(query, params)
        return result[0].get("count", 0) if result else 0

    def table_exists(self, table_name: str) -> bool:
        query = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = %s AND table_schema = 'public'
            )
        """
        result = self.execute_query(query, (table_name,))
        return result[0].get("exists", False) if result else False

    def execute_raw_sql(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        try:
            self.cursor.execute(query, params)
            if self.cursor.description is not None:
                rows = self.cursor.fetchall()
                return [dict(row) for row in rows]
            return []
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения запроса: {e}")
            raise

    def create_table(self, table_name: str, columns_def: str):
        """Создаёт таблицу по определению колонок"""
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
        self.execute_write(query)
        logger.info(f"✅ Таблица {table_name} создана (или уже существует)")

    def drop_table(self, table_name: str):
        """Удаляет таблицу (для тестов)"""
        self.execute_write(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        logger.info(f"🗑️ Таблица {table_name} удалена")


# ============ ПРИМЕР ИСПОЛЬЗОВАНИЯ ============
if __name__ == "__main__":
    print("\n🚀 Тестирование драйвера PostgreSQL...")
    db = PostgresDB()
    with db:
        print("✅ Подключение установлено")
        # Проверяем таблицы
        for table in ["users", "tables", "bookings"]:
            exists = db.table_exists(table)
            print(f"  {table}: {'существует' if exists else 'не существует'}")