# src/controllers/external_data_controller.py
from typing import List, Optional, Dict, Any
from PySide6.QtCore import QObject, Signal

from src.services.external_data_service import ExternalDataService
from src.utils.logger import logger

class ExternalDataController(QObject):
    """
    Controller layer for external real estate data.
    
    Acts as a bridge between the UI/Workers and the ExternalDataService.
    Operates in read-only mode for retrieving products and generating content.
    """
    error_occurred = Signal(str)
    msg_signal = Signal(str)

    def __init__(self, service: ExternalDataService):
        """
        Initializes the ExternalDataController with the provided service.

        Args:
            service (ExternalDataService): The service handling data operations.
        """
        super().__init__()
        self.service = service
    
    def get_by_pid(self, pid: str) -> Optional[Dict[str, Any]]:
        return self.service.get_product_details(pid)

    def get_all_products_display(self) -> List[Dict[str, Any]]:
        """
        Retrieves a list of all products formatted for display purposes.

        Returns:
            List[Dict[str, Any]]: A list of enriched product dictionaries.
        """
        try:
            return self.service.get_all_products_display()
        except Exception as e:
            logger.error(f"Error getting all products: {e}")
            self.error_occurred.emit(str(e))
            return []

    def get_product_pids(self) -> List[str]:
        """
        Retrieves a list of all available Product IDs (PIDs).

        Returns:
            List[str]: A list of existing PIDs.
        """
        try:
            return self.service.get_product_pids()
        except Exception as e:
            logger.error(f"Error getting PIDs: {e}")
            self.error_occurred.emit(str(e))
            return []

    def get_product_details(self, pid: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves detailed information for a specific product by its PID.

        Args:
            pid (str): The product identifier.

        Returns:
            Optional[Dict[str, Any]]: Product details if found, otherwise None.
        """
        try:
            return self.service.get_product_details(pid)
        except Exception as e:
            logger.error(f"Error getting details for PID {pid}: {e}")
            self.error_occurred.emit(str(e))
            return None

    def get_random_product_for_posting(self, transaction_type: int, days: int = 7) -> Optional[Dict[str, Any]]:
        """
        Selects a random product updated within a recent timeframe for automated posting.

        Args:
            transaction_type (int): The transaction category code.
            days (int): The look-back period in days. Defaults to 7.

        Returns:
            Optional[Dict[str, Any]]: A random product dictionary if available, otherwise None.
        """
        try:
            return self.service.get_random_product_for_posting(transaction_type, days)
        except Exception as e:
            logger.error(f"Error getting random product: {e}")
            self.error_occurred.emit(str(e))
            return None

    def get_random_pid(self) -> Optional[str]:
        """
        Retrieves a random PID from recently updated products.

        Returns:
            Optional[str]: A product identifier if found, otherwise None.
        """
        try:
            return self.service.get_random_pid()
        except Exception as e:
            logger.error(f"Error getting random PID: {e}")
            self.error_occurred.emit(str(e))
            return None

    def generate_content_by_pid(self, pid: str) -> Optional[Dict[str, Any]]:
        """
        Generates post content (Title, Description, and Images) based on templates 
        and real product data associated with a PID.

        Args:
            pid (str): The product identifier.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the generated content strings 
                                     and image paths, otherwise None.
        """
        try:
            return self.service.generate_content_by_pid(pid)
        except Exception as e:
            logger.error(f"Error generating content for PID {pid}: {e}")
            self.error_occurred.emit(str(e))
            return None