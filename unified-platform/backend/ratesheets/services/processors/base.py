from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class RateSheetProcessingError(Exception):
    """Exception raised when rate sheet processing fails."""
    pass


class BaseRateSheetProcessor(ABC):
    """
    Abstract base class for rate sheet processors.
    Defines the interface for extracting data from various file formats.
    """
    
    def __init__(self, rate_sheet_instance):
        """
        Initialize with a RateSheet model instance.
        """
        self.rate_sheet = rate_sheet_instance
        self.file_path = rate_sheet_instance.file.path
        
    @abstractmethod
    def process(self) -> Dict[str, Any]:
        """
        Process the file and return extracted data.
        
        Returns:
            Dict containing extraction results/stats.
            Example: {'programs_found': 5, 'adjustments_updated': 20}
        """
        pass
        
    def log(self, message: str):
        """Append a message to the rate sheet log."""
        self.rate_sheet.log += f"{message}\n"
        self.rate_sheet.save(update_fields=['log'])
        logger.info(f"RateSheet {self.rate_sheet.id}: {message}")
