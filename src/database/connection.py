# src/database/connection.py
import re
import os
import sys
import threading
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Tuple
from PySide6.QtSql import QSqlDatabase, QSqlQuery

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from src.database.schema import SQL_SCHEMA
from src.utils.logger import logger
from src.utils.yaml_handler import settings


# =========================
# DATABASE MANAGER
# =========================


class DatabaseManager:
    """
    Production-ready SQLite manager for multi-threaded phone farm systems.
    - Thread-safe (1 unique connection per thread)
    - WAL mode enabled
    - Safe transaction handling
    """

    def __init__(self):
        self.database_path = os.path.join(BASE_DIR, settings.repositories.database_path) # type: ignore
        self._ensure_database_directory()

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------

    def _ensure_database_directory(self):
        """Ensures the directory containing the database exists."""
        db_dir = Path(self.database_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def _generate_connection_name(self) -> str:
        """Generates a unique connection name for the current thread."""
        thread_id = threading.get_ident()
        return f"PHONEFARM_CONN_{thread_id}"

    @property
    def db(self) -> QSqlDatabase:
        connection_name = self._generate_connection_name()

        if QSqlDatabase.contains(connection_name):
            return QSqlDatabase.database(connection_name)

        db = QSqlDatabase.addDatabase("QSQLITE", connection_name)
        db.setDatabaseName(self.database_path)
        return db

    def _ensure_connection(self):
        """Ensures the database is open."""
        if not self.db.isOpen():
            if not self.connect():
                raise Exception("Database connection failed.")

    # --------------------------------------------------
    # Connection lifecycle
    # --------------------------------------------------

    def connect(self) -> bool:
        """Opens the database connection and applies performance PRAGMAs."""
        db = self.db

        if db.isOpen():
            return True

        if not db.open():
            err_text = db.lastError().text()
            logger.failed(f"Database connection failed: {err_text}")

            # Debug: Check available drivers if connection fails
            drivers = QSqlDatabase.drivers()
            logger.debug(f"Available SQL drivers: {drivers}")
            if "QSQLITE" not in drivers:
                logger.error(
                    "CRITICAL: QSQLITE driver is missing. Check PySide6 installation or QCoreApplication initialization."
                )
            return False

        # SQLite performance tuning
        QSqlQuery("PRAGMA journal_mode=WAL;", db).exec()
        QSqlQuery("PRAGMA synchronous=NORMAL;", db).exec()
        QSqlQuery("PRAGMA foreign_keys=ON;", db).exec()
        QSqlQuery("PRAGMA temp_store=MEMORY;", db).exec()
        QSqlQuery("PRAGMA cache_size=10000;", db).exec()

        logger.debug("Database connected and PRAGMAs applied.")
        return True

    def close(self) -> None:
        """Safely closes the connection for the current thread."""
        connection_name = self._generate_connection_name()

        if QSqlDatabase.contains(connection_name):
            db = QSqlDatabase.database(connection_name)
            if db.isOpen():
                db.close()

            del db
            QSqlDatabase.removeDatabase(connection_name)
            logger.debug(f"Connection {connection_name} closed.")

    def is_connected(self) -> bool:
        return self.db.isOpen()

    # --------------------------------------------------
    # Transaction
    # --------------------------------------------------

    def transaction(self) -> bool:
        self._ensure_connection()
        return self.db.transaction()

    def commit(self) -> bool:
        return self.db.commit()

    def rollback(self) -> bool:
        return self.db.rollback()

    @contextmanager
    def atomic(self):
        if not self.transaction():
            logger.error("Failed to start transaction.")
            raise Exception("Cannot start transaction")

        try:
            yield
            if not self.commit():
                raise Exception("Commit failed")
        except Exception as e:
            self.rollback()
            logger.failed(f"Transaction rolled back due to: {e}")
            raise

    # --------------------------------------------------
    # Schema initialization
    # --------------------------------------------------

    def init_tables(self) -> bool:
        try:
            self._ensure_connection()
            existing_tables = self.db.tables()

            with self.atomic():
                for table_sql in SQL_SCHEMA:
                    match = re.search(
                        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?['\"`]?(\w+)['\"`]?",
                        table_sql,
                        re.IGNORECASE,
                    )

                    if match:
                        table_name = match.group(1)
                        if table_name in existing_tables:
                            continue
                    success, error = self.execute(table_sql)
                    if not success:
                        raise Exception(
                            f"Schema initialization failed for {table_sql[:20]}...: {error}"
                        )

            logger.success("Database tables initialized successfully.")
            return True

        except Exception as e:
            logger.error(f"Schema initialization error: {e}")
            return False

    # --------------------------------------------------
    # Query Execution
    # --------------------------------------------------

    def execute(
        self, query_string: str, params: Optional[Any] = None
    ) -> Tuple[bool, str]:
        self._ensure_connection()

        query = QSqlQuery(self.db)
        if params:
            if not query.prepare(query_string):
                error = query.lastError().text()
                logger.error(f"🚨 DB STRUCTURE ERROR (Prepare Error): {error}")
                logger.debug(f"SQL query: {query_string}")
                return False, error
            
            if isinstance(params, dict):
                bind_values = list(params.values())
            else:
                bind_values = params
            for param in bind_values:
                query.addBindValue(param)
                
            success = query.exec()
        else:
            success = query.exec(query_string)

        if not success:
            error = query.lastError().text()
            logger.failed(f"Query execution error: {error}")
            logger.debug(f"SQL: {query_string} | Params: {params}")
            return False, error

        return True, ""

    # --------------------------------------------------
    # Fetch Helpers
    # --------------------------------------------------

    def _record_to_dict(self, query: QSqlQuery) -> Dict[str, Any]:
        record = query.record()
        result = {}
        for i in range(record.count()):
            result[record.fieldName(i)] = query.value(i)
        return result

    def fetch_one(
        self, query_string: str, params: Optional[Tuple] = None
    ) -> Optional[Dict[str, Any]]:
        self._ensure_connection()
        query = QSqlQuery(self.db)
        query.prepare(query_string)
        if params:
            for param in params:
                query.addBindValue(param)

        if query.exec() and query.next():
            return self._record_to_dict(query)
        return None

    def fetch_all(
        self, query_string: str, params: Optional[Tuple] = None
    ) -> List[Dict[str, Any]]:
        self._ensure_connection()
        query = QSqlQuery(self.db)
        query.prepare(query_string)
        if params:
            for param in params:
                query.addBindValue(param)

        results = []
        if query.exec():
            while query.next():
                results.append(self._record_to_dict(query))
        return results
