# src/database/external_schema.py
from src.constants import Database__Table

"""
SQL script containing the table definitions for the application's local database.
Uses SQLite-compatible syntax.
"""

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {Database__Table.REAL_ESTATE_PRODUCTS.value} (
    id VARCHAR PRIMARY KEY,
    pid TEXT,
    status TEXT,
    transaction_type TEXT,
    province TEXT,
    district TEXT,
    ward TEXT,
    street TEXT,
    category TEXT,
    area REAL,
    price REAL,
    unit TEXT,
    legal TEXT,
    structure REAL,
    function TEXT,
    building_line TEXT,
    furniture TEXT,
    description TEXT,
    created_at TEXT,
    updated_at TEXT
);
CREATE TABLE IF NOT EXISTS {Database__Table.REAL_ESTATE_TEMPLATES.value} (
    id VARCHAR PRIMARY KEY,
    transaction_type TEXT,
    name TEXT,
    category TEXT,
    value TEXT,
    is_default BOOLEAN,
    created_at TEXT,
    updated_at TEXT
);
"""