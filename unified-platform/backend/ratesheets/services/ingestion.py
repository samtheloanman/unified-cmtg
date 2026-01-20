"""
Rate sheet data ingestion service.

This module handles the ingestion of extracted rate sheet data into the
pricing database, creating and updating RateAdjustment records.
"""

import json
import logging
from decimal import Decimal
from typing import Any, Dict, List

from django.db import transaction

from pricing.models import (
    Lender,
    LenderProgramOffering,
    ProgramType,
    RateAdjustment,
)

logger = logging.getLogger(__name__)


class IngestionError(Exception):
    """Exception raised when data ingestion fails."""
    pass


@transaction.atomic
def update_pricing_from_extraction(lender, extracted_data):
    """
    Update pricing data from extracted rate sheet information.

    Supports both legacy format (JSON string) and new format (dict).

    Args:
        lender (Lender): Lender instance
        extracted_data: Either:
            - JSON string (legacy format)
            - Dictionary with structure:
                {
                    'metadata': {...},
                    'programs': [...],
                    'adjustments': [...]
                }

    Returns:
        str or dict: Summary of ingestion results
    """
    logger.info(f"Starting ingestion for lender: {lender.company_name}")

    # Handle legacy JSON string format
    if isinstance(extracted_data, str):
        return _handle_legacy_format(lender, extracted_data)

    # Handle new dictionary format
    if not isinstance(extracted_data, dict):
        error_msg = f"Invalid data type: {type(extracted_data)}"
        logger.error(error_msg)
        return {'error': error_msg}

    stats = {
        'programs_processed': 0,
        'programs_created': 0,
        'programs_updated': 0,
        'adjustments_created': 0,
        'adjustments_updated': 0,
        'errors': []
    }

    try:
        # Process programs
        programs = extracted_data.get('programs', [])
        for program_data in programs:
            try:
                result = _ingest_program(lender, program_data)
                stats['programs_processed'] += 1
                if result['created']:
                    stats['programs_created'] += 1
                else:
                    stats['programs_updated'] += 1

                # Process adjustments for this program
                offering = result['offering']
                program_adjustments = extracted_data.get('adjustments', [])
                adj_stats = _ingest_adjustments(offering, program_adjustments)
                stats['adjustments_created'] += adj_stats['created']
                stats['adjustments_updated'] += adj_stats['updated']

            except Exception as e:
                error_msg = f"Error processing program '{program_data.get('program_name')}': {str(e)}"
                logger.error(error_msg)
                stats['errors'].append(error_msg)

        logger.info(f"Ingestion completed: {stats}")
        return stats

    except Exception as e:
        error_msg = f"Ingestion failed: {str(e)}"
        logger.error(error_msg)
        return {'error': error_msg, 'details': str(e)}


def _handle_legacy_format(lender, extracted_json_string):
    """
    Handle legacy JSON string format.

    Args:
        lender: Lender instance
        extracted_json_string: JSON string

    Returns:
        str: Summary message
    """
    if not extracted_json_string:
        logger.warning(f"No data passed for lender {lender.company_name}.")
        return "No data extracted."

    try:
        data = json.loads(extracted_json_string)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON for {lender.company_name}: {e}")
        return f"Error: Invalid JSON format. Details: {e}"

    if not isinstance(data, list):
        logger.error(f"JSON data for {lender.company_name} is not a list.")
        return "Error: JSON data must be a list of adjustment objects."

    adjustments_created = 0
    programs_created = 0

    # Group adjustments by program_name
    programs = {}
    for item in data:
        program_name = item.get("program_name")
        if not program_name:
            continue
        if program_name not in programs:
            programs[program_name] = []
        programs[program_name].append(item)

    for program_name, adjustments in programs.items():
        # Find or create ProgramType
        program_type, created = ProgramType.objects.get_or_create(
            name=program_name,
            defaults={
                'category': 'non_qm',
                'base_min_fico': 600,
                'base_max_ltv': 80,
            }
        )
        if created:
            programs_created += 1

        # Find or create LenderProgramOffering
        offering, _ = LenderProgramOffering.objects.get_or_create(
            lender=lender,
            program_type=program_type,
            defaults={
                'min_rate': 3.0,
                'max_rate': 15.0,
                'min_fico': 500,
                'max_ltv': 90,
            }
        )

        # Clear old FICO/LTV adjustments
        offering.adjustments.filter(
            adjustment_type=RateAdjustment.ADJUSTMENT_TYPE_FICO_LTV
        ).delete()

        # Create new adjustments
        new_adjustments = []
        for adj_data in adjustments:
            new_adjustments.append(
                RateAdjustment(
                    offering=offering,
                    adjustment_type=RateAdjustment.ADJUSTMENT_TYPE_FICO_LTV,
                    row_min=adj_data.get("min_fico"),
                    row_max=adj_data.get("max_fico"),
                    col_min=adj_data.get("min_ltv"),
                    col_max=adj_data.get("max_ltv"),
                    adjustment_points=adj_data.get("adjustment"),
                )
            )

        if new_adjustments:
            RateAdjustment.objects.bulk_create(new_adjustments, batch_size=1000)
            adjustments_created += len(new_adjustments)

    summary = (
        f"Processing complete for {lender.company_name}. "
        f"Programs created: {programs_created}. "
        f"Adjustments created: {adjustments_created}."
    )
    logger.info(summary)
    return summary


def _ingest_program(lender, program_data):
    """
    Ingest a single program.

    Args:
        lender: Lender instance
        program_data: Program dictionary

    Returns:
        Dictionary with 'offering' and 'created' flag
    """
    program_name = program_data['program_name']
    program_type_name = program_data.get('program_type', 'conventional')

    # Get or create ProgramType
    program_type, _ = ProgramType.objects.get_or_create(
        name=program_name,
        defaults={
            'category': _map_program_type_to_category(program_type_name),
            'loan_type': program_type_name,
            'property_types': program_data.get('property_types', ['residential']),
            'base_min_fico': program_data.get('min_fico', 620),
            'base_max_ltv': program_data.get('max_ltv', 80.0),
        }
    )

    # Get or create LenderProgramOffering
    offering, created = LenderProgramOffering.objects.get_or_create(
        lender=lender,
        program_type=program_type,
        defaults={
            'min_rate': program_data.get('base_rate', 6.0),
            'max_rate': program_data.get('base_rate', 6.0) + 1.0,
            'min_points': 0,
            'max_points': 2,
            'min_fico': program_data.get('min_fico', 620),
            'max_ltv': program_data.get('max_ltv', 80.0),
            'min_loan': Decimal(str(program_data.get('min_loan_amount', 75000))),
            'max_loan': Decimal(str(program_data.get('max_loan_amount', 2000000))),
        }
    )

    if not created:
        # Update existing offering
        offering.min_rate = program_data.get('base_rate', offering.min_rate)
        offering.max_rate = program_data.get('base_rate', offering.max_rate) + 1.0
        offering.min_fico = program_data.get('min_fico', offering.min_fico)
        offering.max_ltv = program_data.get('max_ltv', offering.max_ltv)
        offering.save()

    logger.info(
        f"{'Created' if created else 'Updated'} offering: "
        f"{lender.company_name} - {program_name}"
    )

    return {'offering': offering, 'created': created}


def _ingest_adjustments(offering, adjustments_data):
    """
    Ingest adjustments for a program offering.

    Args:
        offering: LenderProgramOffering instance
        adjustments_data: List of adjustment dictionaries

    Returns:
        Dictionary with 'created' and 'updated' counts
    """
    stats = {'created': 0, 'updated': 0}

    for adj_data in adjustments_data:
        try:
            adjustment_type = adj_data['adjustment_type']
            adjustment_points = float(adj_data['adjustment_points'])

            # Build lookup criteria
            lookup = {
                'offering': offering,
                'adjustment_type': adjustment_type,
            }

            # Add type-specific fields
            if 'value_key' in adj_data:
                lookup['value_key'] = adj_data['value_key']

            if 'row_min' in adj_data and adj_data['row_min'] is not None:
                lookup['row_min'] = float(adj_data['row_min'])
                lookup['row_max'] = float(adj_data.get('row_max', adj_data['row_min']))

            if 'col_min' in adj_data and adj_data['col_min'] is not None:
                lookup['col_min'] = float(adj_data['col_min'])
                lookup['col_max'] = float(adj_data.get('col_max', adj_data['col_min']))

            # Create or update adjustment
            adjustment, created = RateAdjustment.objects.update_or_create(
                **lookup,
                defaults={'adjustment_points': adjustment_points}
            )

            if created:
                stats['created'] += 1
            else:
                stats['updated'] += 1

        except Exception as e:
            logger.error(f"Error ingesting adjustment: {str(e)}")
            continue

    return stats


def _map_program_type_to_category(program_type: str) -> str:
    """
    Map program type string to category.

    Args:
        program_type: Program type string

    Returns:
        Category string
    """
    program_type_lower = program_type.lower()

    if program_type_lower in ['fha', 'va', 'usda', 'conventional']:
        return 'agency'
    elif program_type_lower in ['dscr', 'bank_statement', 'asset_depletion']:
        return 'non_qm'
    elif program_type_lower in ['hard_money', 'fix_and_flip', 'bridge']:
        return 'hard_money'
    elif program_type_lower in ['commercial']:
        return 'commercial'
    else:
        return 'non_qm'  # Default
