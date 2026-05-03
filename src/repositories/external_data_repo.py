# src/repositories/external_data_repo.py
import sqlite3
from typing import List, Optional
from datetime import datetime, timedelta

from src.constants import (
    RealEstateTemplate__Name,
    RealEstateProduct__TransactionType,
    RealEstateProduct__Category,
    Database__Table,
)
from src.entities import (
    RealEstateProduct,
    RealEstateTemplate,
)
from src.utils.logger import logger
from src.utils.yaml_handler import settings


class ExternalDataRepository:
    """
    Repository for interacting with the external SQLite database.
    
    This repository operates in read-only mode to fetch real estate products 
    and content templates used for automation tasks.
    """

    def __init__(self):
        """
        Initializes the repository using paths defined in the system settings.
        """
        self.db_path = settings.repositories.external_db_path  # type: ignore
        self.image_container_dir = settings.repositories.external_img_dir # type: ignore

    def _get_connection(self):
        """
        Establishes a read-only connection to the SQLite database.
        
        Returns:
            sqlite3.Connection: A connection object with row_factory set to sqlite3.Row.
        """
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    # ======================================================
    # HELPER MAPPERS (Row -> Object)
    # ======================================================

    def _map_row_to_product(self, row: sqlite3.Row) -> RealEstateProduct:
        """
        Maps a database row to a RealEstateProduct entity.
        """
        return RealEstateProduct(
            id=row["id"],
            pid=row["pid"],
            status=bool(row["status"]),
            transaction_type=row["transaction_type"],
            province=row["province"],
            district=row["district"],
            ward=row["ward"],
            street=row["street"],
            category=row["category"],
            area=row["area"],
            price=row["price"],
            legal=row["legal"],
            structure=row["structure"],
            function=row["function"],
            building_line=row["building_line"],
            furniture=row["furniture"],
            description=row["description"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _map_row_to_template(self, row: sqlite3.Row) -> RealEstateTemplate:
        """
        Maps a database row to a RealEstateTemplate entity.
        """
        return RealEstateTemplate(
            id=row["id"],
            transaction_type=row["transaction_type"],
            name=row["name"],
            category=row["category"],
            value=row["value"],
            is_default=bool(row["is_default"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    # ======================================================
    # PRODUCT METHODS
    # ======================================================

    def get_all_products(self) -> List[RealEstateProduct]:
        """
        Retrieves all products from the database.
        
        Returns:
            List[RealEstateProduct]: A list of all real estate products.
        """
        results = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {Database__Table.REAL_ESTATE_PRODUCTS.value}")
                rows = cursor.fetchall()
                for row in rows:
                    results.append(self._map_row_to_product(row))
        except Exception as e:
            logger.error(f"[ExternalRepo] Error getting all products: {e}")
        return results

    def get_all_pid(self) -> List[str]:
        """
        Retrieves a list of all product IDs (PID).
        
        Returns:
            List[str]: A list of strings containing all product PIDs.
        """
        results = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT pid FROM {Database__Table.REAL_ESTATE_PRODUCTS.value}")
                rows = cursor.fetchall()
                for row in rows:
                    if row["pid"]:
                        results.append(row["pid"])
        except Exception as e:
            logger.error(f"[ExternalRepo] Error getting PIDs: {e}")
        return results

    def get_one_product(self, pid: str) -> Optional[RealEstateProduct]:
        """
        Retrieves a single product details by its PID.
        
        Args:
            pid (str): The product ID to search for.
            
        Returns:
            Optional[RealEstateProduct]: The product object if found, else None.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {Database__Table.REAL_ESTATE_PRODUCTS.value} WHERE pid = ?", (pid,))
                row = cursor.fetchone()
                if row:
                    return self._map_row_to_product(row)
        except Exception as e:
            logger.error(f"[ExternalRepo] Error getting product {pid}: {e}")
        return None

    def get_one_recent_product(self, transaction_type, recent_day: int = 7) -> Optional[RealEstateProduct]:
        """
        Lấy một sản phẩm ngẫu nhiên được cập nhật gần đây.
        Sử dụng SQL function để tính toán thời gian, giúp logic đồng bộ với các hàm query đơn lẻ khác.
        """
        # 1. Chuẩn hóa transaction_type về chuỗi (TEXT) để khớp với Database
        if isinstance(transaction_type, int):
            try:
                t_val = list(RealEstateProduct__TransactionType)[transaction_type].value
            except (IndexError, ValueError):
                t_val = RealEstateProduct__TransactionType.SALE.value
        else:
            t_val = transaction_type.value if hasattr(transaction_type, 'value') else str(transaction_type)

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = f"""
                    SELECT * FROM {Database__Table.REAL_ESTATE_PRODUCTS.value} 
                    WHERE transaction_type = ? 
                    AND updated_at >= datetime('now', 'localtime', '-{int(recent_day)} days') 
                    ORDER BY RANDOM() LIMIT 1
                """
                
                cursor.execute(query, (t_val,))
                row = cursor.fetchone()
                if row:
                    return self._map_row_to_product(row)
                    
        except Exception as e:
            logger.error(f"[ExternalRepo] Error getting recent product: {e}")
            
        return None
    
    # ======================================================
    # TEMPLATE METHODS
    # ======================================================

    def get_all_templates(self) -> List[dict]:
        """
        Retrieves all templates from the database as a list of dictionaries.
        
        Returns:
            List[dict]: A list of dictionary objects representing templates.
        """
        results = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM real_estate_templates")
                rows = cursor.fetchall()
                for row in rows:
                    results.append(dict(row))
        except Exception as e:
            logger.error(f"[ExternalRepo] Error getting templates: {e}")
        return results

    def get_default_template(
        self, name: RealEstateTemplate__Name, transaction_type: RealEstateProduct__TransactionType, category: RealEstateProduct__Category,
    ) -> Optional[RealEstateTemplate]:
        """
        Retrieves the default template for a specific transaction type and content part.
        
        Args:
            transaction_type (int): The transaction category.
            part (int): The content part identifier (e.g., Title, Description).
            
        Returns:
            Optional[RealEstateTemplate]: The default template if found, else None.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = f"""
                    SELECT * FROM {Database__Table.REAL_ESTATE_TEMPLATES.value}
                    WHERE transaction_type = ? AND name = ? AND category = ? AND is_default = 1
                    LIMIT 1
                """
                cursor.execute(query, (transaction_type, name, category))
                row = cursor.fetchone()
                if row:
                    return self._map_row_to_template(row)
        except Exception as e:
            logger.error(f"[ExternalRepo] Error getting default template: {e}")
        return None

    def get_random_template(
        self, name: RealEstateTemplate__Name, transaction_type: RealEstateProduct__TransactionType, category: RealEstateProduct__Category,
    ) -> Optional[RealEstateTemplate]:
        """
        Retrieves a random template matching the transaction type, category, and content part.
        
        Args:
            transaction_type (int): The transaction category.
            category (int): The real estate category (e.g., Apartment, House).
            part (int): The content part identifier.
            
        Returns:
            Optional[RealEstateTemplate]: A random matching template if found, else None.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = f"""
                    SELECT * FROM {Database__Table.REAL_ESTATE_TEMPLATES.value} 
                    WHERE transaction_type = ? AND name = ? AND category = ? AND is_default = 0
                    ORDER BY RANDOM() LIMIT 1
                """
                cursor.execute(query, (transaction_type, name, category))
                row = cursor.fetchone()
                if row:
                    return self._map_row_to_template(row)
        except Exception as e:
            logger.error(f"[ExternalRepo] Error getting random template: {e}")
        return None