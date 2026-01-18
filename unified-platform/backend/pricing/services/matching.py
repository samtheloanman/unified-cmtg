"""
Loan matching service.

This module provides functionality to match borrower qualifications
against available lender program offerings.

Ported from legacy cmtgdirect/loans/queries.py
"""

from typing import Any, Dict

from django.db.models import QuerySet

from pricing.models import LenderProgramOffering, LoanProgram, QualifyingInfo


class QualifyingInfoDTO:
    """
    Borrower qualification information for loan matching (DTO).

    This is a simple data class that holds the criteria used to
    match against lender program offerings.
    """

    def __init__(
        self,
        property_type: str,
        entity_type: str,
        purpose: str,
        occupancy: str,
        state: str,
        loan_amount: float,
        ltv: float,
        estimated_credit_score: int,
    ):
        """Initialize qualifying info with borrower details."""
        self.property_type = property_type
        self.entity_type = entity_type
        self.purpose = purpose
        self.occupancy = occupancy
        self.state = state
        self.loan_amount = loan_amount
        self.ltv = ltv
        self.estimated_credit_score = estimated_credit_score


def _get_filters_for_loan_program_match_by_qual(
    qi: QualifyingInfoDTO
) -> Dict[str, Any]:
    """
    Build filter dictionary for LenderProgramOffering matching.

    Args:
        qi: QualifyingInfoDTO object with borrower qualification details

    Returns:
        Dictionary of filters for Django QuerySet .filter()
    """
    filters = {
        # ProgramType fields (via foreign key)
        'program_type__property_types__contains': [qi.property_type],
        'program_type__entity_types__contains': [qi.entity_type],
        'program_type__purposes__contains': [qi.purpose],
        'program_type__occupancy__contains': [qi.occupancy],

        # Lender fields (via foreign key)
        'lender__include_states__contains': [qi.state],

        # LenderProgramOffering numeric limits
        'min_loan__lte': qi.loan_amount,          # Loan amount >= min
        'max_loan__gte': qi.loan_amount,          # Loan amount <= max
        'max_ltv__gte': qi.ltv,                   # LTV <= lender max
        'min_fico__lte': qi.estimated_credit_score,  # FICO >= lender min

        # Ensure active
        'is_active': True
    }

    # Note: Legacy logic for property_sub_categories, cost_of_rehab, etc.
    # needs to be migrated to ProgramType/LenderProgramOffering if critical.
    # For now, we rely on the main filters above.

    return filters


def get_matched_loan_programs_for_qual(
    qi: QualifyingInfoDTO
) -> QuerySet[LenderProgramOffering]:
    """
    Find matching LenderProgramOffering objects for a qualification.

    Args:
        qi: QualifyingInfoDTO object with borrower qualification details

    Returns:
        QuerySet of matching LenderProgramOffering objects,
        ordered by lowest rate first
    """
    filters = _get_filters_for_loan_program_match_by_qual(qi)

    # Return LenderProgramOfferings ordered by lowest rate
    return LenderProgramOffering.objects.filter(
        **filters
    ).select_related(
        'lender',
        'program_type'
    ).order_by('min_rate')


def get_quals_for_loan_program(offering: LenderProgramOffering) -> QuerySet:
    """
    Get qualifying info records that match a lender program offering.

    This function performs reverse matching: finding potential borrower
    qualifications (leads) that would be eligible for this specific
    lender program offering.

    Args:
        offering: LenderProgramOffering instance

    Returns:
        QuerySet of matching QualifyingInfo objects
    """
    return QualifyingInfo.objects.filter(
        # Numeric limits
        loan_amount__gte=offering.min_loan,
        loan_amount__lte=offering.max_loan,
        ltv__lte=offering.max_ltv,
        estimated_credit_score__gte=offering.min_fico,

        # Exact match (single value in list of choices)
        state__in=offering.lender.include_states,
        property_type__in=offering.program_type.property_types,
        entity_type__in=offering.program_type.entity_types,
        purpose__in=offering.program_type.purposes,
        occupancy__in=offering.program_type.occupancy,
    )


class LoanMatchingService:
    """
    Service class for loan matching operations.

    Provides a clean interface for matching borrower qualifications
    against available lender programs.
    """

    @staticmethod
    def match_programs(qualification_data: Dict[str, Any]) -> QuerySet:
        """
        Match loan programs based on qualification data.

        Args:
            qualification_data: Dictionary containing:
                - property_type: str
                - entity_type: str
                - purpose: str
                - occupancy: str
                - state: str
                - loan_amount: float
                - ltv: float
                - estimated_credit_score: int

        Returns:
            QuerySet of matching LenderProgramOffering objects
        """
        qi = QualifyingInfoDTO(
            property_type=qualification_data['property_type'],
            entity_type=qualification_data['entity_type'],
            purpose=qualification_data['purpose'],
            occupancy=qualification_data['occupancy'],
            state=qualification_data['state'],
            loan_amount=qualification_data['loan_amount'],
            ltv=qualification_data['ltv'],
            estimated_credit_score=qualification_data['estimated_credit_score']
        )

        return get_matched_loan_programs_for_qual(qi)

    @staticmethod
    def get_best_rates(
        qualification_data: Dict[str, Any],
        limit: int = 10
    ) -> QuerySet:
        """
        Get the best rates for a qualification.

        Args:
            qualification_data: Borrower qualification details
            limit: Maximum number of results to return

        Returns:
            QuerySet of top matching programs by rate
        """
        matches = LoanMatchingService.match_programs(qualification_data)
        return matches[:limit]

    @staticmethod
    def get_adjusted_rate(
        offering: LenderProgramOffering,
        fico: int,
        ltv: float
    ) -> Dict[str, Any]:
        """
        Calculate the adjusted rate/points for a specific FICO/LTV.

        Queries RateAdjustment records that match the borrower's
        FICO score and LTV, then applies them to the base rate.

        Args:
            offering: LenderProgramOffering instance
            fico: Borrower's FICO score
            ltv: Loan-to-value ratio (as percentage, e.g., 80.0)

        Returns:
            Dictionary with adjusted_rate and total_points
        """
        from pricing.models import RateAdjustment

        base_rate = float(offering.min_rate)
        total_points = 0.0

        # Get FICO/LTV grid adjustments
        fico_ltv_adjustments = RateAdjustment.objects.filter(
            offering=offering,
            adjustment_type=RateAdjustment.ADJUSTMENT_TYPE_FICO_LTV,
            row_min__lte=fico,
            row_max__gte=fico,
            col_min__lte=ltv,
            col_max__gte=ltv
        )

        for adj in fico_ltv_adjustments:
            total_points += float(adj.adjustment_points)

        return {
            'base_rate': base_rate,
            'adjusted_rate': base_rate,  # Rate adjustments are typically in points
            'total_points': round(total_points, 3),
            'adjustments_applied': fico_ltv_adjustments.count()
        }

    @staticmethod
    def get_quotes_with_adjustments(
        qualification_data: Dict[str, Any],
        limit: int = 10
    ) -> list:
        """
        Get quotes with FICO/LTV adjustments applied.

        This is the main method for getting real pricing.

        Args:
            qualification_data: Borrower qualification details
            limit: Maximum number of results

        Returns:
            List of quote dictionaries with adjusted pricing
        """
        matches = LoanMatchingService.match_programs(qualification_data)[:limit]
        fico = qualification_data['estimated_credit_score']
        ltv = qualification_data['ltv']

        quotes = []
        for offering in matches:
            adjusted = LoanMatchingService.get_adjusted_rate(offering, fico, ltv)
            quotes.append({
                'lender': offering.lender.company_name,
                'program': offering.program_type.name,
                'base_rate': adjusted['base_rate'],
                'adjusted_rate': adjusted['adjusted_rate'],
                'points': adjusted['total_points'],
                'adjustments_applied': adjusted['adjustments_applied'],
                'min_loan': float(offering.min_loan),
                'max_loan': float(offering.max_loan),
            })

        return quotes
