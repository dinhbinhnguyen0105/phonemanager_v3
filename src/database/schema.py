# src/database/schema.py
SQL_SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS devices (
        uuid VARCHAR(36) PRIMARY KEY,
        device_id VARCHAR(255),
        device_name VARCHAR(255) DEFAULT 'New device',
        device_status VARCHAR(50) DEFAULT 'OFFLINE',
        device_root INT DEFAULT 0,
        created_at INTEGER,
        updated_at INTEGER
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS socials (
        uuid VARCHAR(36) PRIMARY KEY,
        user_uuid VARCHAR(36),
        social_id VARCHAR(255),
        social_name VARCHAR(255) DEFAULT 'New social',
        social_password VARCHAR(255),
        social_status INT DEFAULT 0,
        social_group INT DEFAULT 0,
        social_platform VARCHAR(50) DEFAULT 'facebook',
        created_at INTEGER,
        updated_at INTEGER,
        CONSTRAINT fk_social_user FOREIGN KEY (user_uuid) REFERENCES users(uuid) ON DELETE SET NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS users (
        uuid VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(255),
        user_name VARCHAR(255) DEFAULT 'New profile',
        user_status VARCHAR(50) DEFAULT 'INACTIVE',
        device_uuid VARCHAR(36),
        created_at INTEGER,
        updated_at INTEGER,
        CONSTRAINT fk_user_device FOREIGN KEY (device_uuid) REFERENCES devices(uuid) ON DELETE SET NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS proxies (
        uuid VARCHAR(36) PRIMARY KEY,
        host VARCHAR(255) DEFAULT '',
        port INTEGER DEFAULT 0,
        username VARCHAR(255) DEFAULT '',
        password VARCHAR(255) DEFAULT '',
        rotate_url TEXT DEFAULT '',
        proxy_type VARCHAR(50) DEFAULT 'STATIC',
        proxy_status VARCHAR(50) DEFAULT 'AVAILABLE',
        created_at INTEGER,
        updated_at INTEGER
    );
    """
]