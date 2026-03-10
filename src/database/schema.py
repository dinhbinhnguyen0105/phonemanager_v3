# src/database/schema.py
SQL_SCHEMA = [
    """
CREATE TABLE devices (
    uuid VARCHAR(36) PRIMARY KEY,
    device_id VARCHAR(255),
    device_name VARCHAR(255) DEFAULT 'New device',
    device_status VARCHAR(50) DEFAULT 'OFFLINE',
    device_root INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""",
"""
CREATE TABLE socials (
    uuid VARCHAR(36) PRIMARY KEY,
    social_id VARCHAR(255),
    social_name VARCHAR(255) DEFAULT 'New social',
    social_password VARCHAR(255),
    social_status INT DEFAULT 0,
    social_group INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""",

"""
CREATE TABLE users (
    uuid VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255),
    user_name VARCHAR(255) DEFAULT 'New profile',
    user_status VARCHAR(50) DEFAULT 'INACTIVE',
    device_uuid VARCHAR(36),
    social_uuid VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_device FOREIGN KEY (device_uuid) REFERENCES devices(uuid) ON DELETE SET NULL,
    CONSTRAINT fk_user_social FOREIGN KEY (social_uuid) REFERENCES socials(uuid) ON DELETE SET NULL
);
""",

"""
CREATE TABLE proxies (
    proxy_id SERIAL PRIMARY KEY,
    value VARCHAR(255) DEFAULT '',
    proxy_type VARCHAR(50) DEFAULT 'STATIC',
    proxy_status VARCHAR(50) DEFAULT 'AVAILABLE'
);
""",
]