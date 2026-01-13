"""
Rate sheet processor factory.

This module provides a factory for selecting and instantiating the appropriate
rate sheet processor based on configuration, file type, or lender-specific rules.
"""

import logging
from typing import Optional, Type

from django.conf import settings

from .base import BaseRateSheetProcessor
from .pdf_plumber import PdfPlumberProcessor

logger = logging.getLogger(__name__)

# Import GeminiAIProcessor only if dependencies are available
try:
    from .gemini_ai import GeminiAIProcessor
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("GeminiAIProcessor not available - missing dependencies")


class ProcessorRegistry:
    """
    Registry of available rate sheet processors.

    Maintains a mapping of processor names to processor classes,
    and provides selection logic based on various criteria.
    """

    def __init__(self):
        self._processors = {}
        self._register_default_processors()

    def _register_default_processors(self):
        """Register built-in processors."""
        # Always available
        self.register('pdf_plumber', PdfPlumberProcessor)

        # Only if dependencies installed
        if GEMINI_AVAILABLE:
            self.register('gemini_ai', GeminiAIProcessor)

    def register(self, name: str, processor_class: Type[BaseRateSheetProcessor]):
        """
        Register a processor.

        Args:
            name: Unique processor identifier
            processor_class: Processor class (must extend BaseRateSheetProcessor)
        """
        if not issubclass(processor_class, BaseRateSheetProcessor):
            raise ValueError(
                f"Processor {processor_class} must extend BaseRateSheetProcessor"
            )

        self._processors[name] = processor_class
        logger.info(f"Registered processor: {name}")

    def get_processor(self, name: str) -> Optional[Type[BaseRateSheetProcessor]]:
        """
        Get a processor by name.

        Args:
            name: Processor identifier

        Returns:
            Processor class or None if not found
        """
        return self._processors.get(name)

    def list_processors(self):
        """
        List all registered processors.

        Returns:
            Dictionary of processor names to classes
        """
        return self._processors.copy()

    def get_default_processor(self, rate_sheet) -> Type[BaseRateSheetProcessor]:
        """
        Get the default processor for a rate sheet.

        Selection logic:
        1. If GOOGLE_API_KEY is configured and file is PDF, use GeminiAIProcessor
        2. Otherwise, use PdfPlumberProcessor

        Args:
            rate_sheet: RateSheet model instance

        Returns:
            Processor class
        """
        # Check for Google API key
        google_api_key = getattr(settings, 'GOOGLE_API_KEY', None)
        is_pdf = rate_sheet.file.name.lower().endswith('.pdf')

        # Prefer AI processor if available and configured
        if google_api_key and is_pdf and GEMINI_AVAILABLE:
            logger.info(
                f"Selected GeminiAIProcessor for rate sheet {rate_sheet.id}"
            )
            return GeminiAIProcessor

        # Fallback to PdfPlumber
        logger.info(
            f"Selected PdfPlumberProcessor for rate sheet {rate_sheet.id}"
        )
        return PdfPlumberProcessor

    def get_processor_for_lender(
        self,
        rate_sheet,
        lender_processor_map: Optional[dict] = None
    ) -> Type[BaseRateSheetProcessor]:
        """
        Get processor based on lender-specific rules.

        This allows different lenders to use different processors if needed.
        For example, some lenders may have rate sheets that work better with
        specific processors.

        Args:
            rate_sheet: RateSheet model instance
            lender_processor_map: Optional mapping of lender IDs to processor names

        Returns:
            Processor class
        """
        if lender_processor_map:
            lender_id = rate_sheet.lender.id
            processor_name = lender_processor_map.get(lender_id)

            if processor_name:
                processor = self.get_processor(processor_name)
                if processor:
                    logger.info(
                        f"Using lender-specific processor {processor_name} "
                        f"for rate sheet {rate_sheet.id}"
                    )
                    return processor

        # Fall back to default
        return self.get_default_processor(rate_sheet)


# Global registry instance
registry = ProcessorRegistry()


def get_processor_for_rate_sheet(
    rate_sheet,
    processor_name: Optional[str] = None,
    lender_processor_map: Optional[dict] = None
) -> BaseRateSheetProcessor:
    """
    Factory function to get the appropriate processor instance for a rate sheet.

    Args:
        rate_sheet: RateSheet model instance
        processor_name: Optional explicit processor name to use
        lender_processor_map: Optional mapping of lender IDs to processor names

    Returns:
        Instantiated processor ready to use

    Raises:
        ValueError: If specified processor is not found

    Example:
        >>> processor = get_processor_for_rate_sheet(rate_sheet)
        >>> result = processor.process()

        >>> # Use specific processor
        >>> processor = get_processor_for_rate_sheet(
        ...     rate_sheet,
        ...     processor_name='gemini_ai'
        ... )

        >>> # Use lender-specific mapping
        >>> lender_map = {1: 'gemini_ai', 2: 'pdf_plumber'}
        >>> processor = get_processor_for_rate_sheet(
        ...     rate_sheet,
        ...     lender_processor_map=lender_map
        ... )
    """
    # If explicit processor name provided, use it
    if processor_name:
        processor_class = registry.get_processor(processor_name)
        if not processor_class:
            raise ValueError(f"Processor '{processor_name}' not found in registry")

        logger.info(
            f"Using explicitly requested processor {processor_name} "
            f"for rate sheet {rate_sheet.id}"
        )
        return processor_class(rate_sheet)

    # If lender mapping provided, use it
    if lender_processor_map:
        processor_class = registry.get_processor_for_lender(
            rate_sheet,
            lender_processor_map
        )
        return processor_class(rate_sheet)

    # Use default selection logic
    processor_class = registry.get_default_processor(rate_sheet)
    return processor_class(rate_sheet)
