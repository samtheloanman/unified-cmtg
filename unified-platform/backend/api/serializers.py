"""
API Serializers

Serializers for REST API endpoints.
"""

from rest_framework import serializers
from applications.models import Application
from loans.models import LoanProgram, Lender


class LeadSubmitSerializer(serializers.Serializer):
    """
    Serializer for lead submission to Floify.

    Used when a borrower clicks "Apply Now" after getting quotes.
    """

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    # Loan details
    loan_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True
    )
    property_address = serializers.CharField(required=False, allow_blank=True)
    property_state = serializers.CharField(max_length=2, required=False, allow_blank=True)
    loan_purpose = serializers.CharField(max_length=50, required=False, allow_blank=True)
    property_type = serializers.CharField(max_length=50, required=False, allow_blank=True)

    # Selected program from quotes
    selected_program = serializers.CharField(required=False, allow_blank=True)
    selected_lender = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        """Ensure email is valid and not empty."""
        if not value or '@' not in value:
            raise serializers.ValidationError("Valid email address is required")
        return value.lower()

    def validate_phone(self, value):
        """Clean phone number format."""
        if value:
            # Remove common separators
            cleaned = ''.join(c for c in value if c.isdigit() or c == '+')
            return cleaned
        return value


class ApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for Application model.

    Used for displaying applications in borrower dashboard.
    """

    full_name = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_color = serializers.CharField(source='status_display_color', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'floify_id',
            'floify_loan_id',
            'full_name',
            'borrower_email',
            'borrower_phone',
            'loan_amount',
            'property_address',
            'property_state',
            'loan_purpose',
            'property_type',
            'selected_program',
            'selected_lender',
            'status',
            'status_display',
            'status_color',
            'created_at',
            'status_updated_at',
        ]
        read_only_fields = [
            'id',
            'floify_id',
            'floify_loan_id',
            'created_at',
            'status_updated_at',
        ]


class ApplicationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for application listing.

    Used for list views with minimal data.
    """

    full_name = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'full_name',
            'loan_amount',
            'selected_program',
            'status',
            'status_display',
            'created_at',
        ]


class LenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lender
        fields = ['id', 'company_name', 'include_states', 'company_website']


class LoanProgramSerializer(serializers.ModelSerializer):
    lender = LenderSerializer(read_only=True)
    lender_id = serializers.PrimaryKeyRelatedField(
        queryset=Lender.objects.all(), source='lender', write_only=True
    )
    class Meta:
        model = LoanProgram
        fields = '__all__'


class LoanProgramListSerializer(serializers.ModelSerializer):
    lender_name = serializers.CharField(source='lender.company_name', read_only=True)
    class Meta:
        model = LoanProgram
        fields = ['id', 'name', 'lender_name', 'loan_type', 'min_loan_amount', 'min_credit', 'potential_rate_min']


class QualificationRequestSerializer(serializers.Serializer):
    loan_amount = serializers.IntegerField(min_value=10000)
    property_value = serializers.IntegerField(min_value=10000)
    loan_purpose = serializers.CharField()
    property_type = serializers.CharField()
    property_state = serializers.CharField(max_length=2)
    occupancy = serializers.CharField()
    credit_score = serializers.IntegerField(min_value=300, max_value=850)
    
    def validate(self, data):
        loan_amount = data.get('loan_amount', 0)
        property_value = data.get('property_value', 1)
        ltv = (loan_amount / property_value) * 100
        data['calculated_ltv'] = round(ltv, 2)
        return data


class QualificationResultSerializer(serializers.Serializer):
    class MatchedProgramSerializer(serializers.Serializer):
        program_id = serializers.IntegerField()
        program_name = serializers.CharField()
        lender_name = serializers.CharField()
        estimated_rate_range = serializers.CharField()
        match_score = serializers.IntegerField()
        notes = serializers.ListField(child=serializers.CharField(), required=False)
    
    matched_programs = MatchedProgramSerializer(many=True)
    total_matches = serializers.IntegerField()
    calculated_ltv = serializers.FloatField()

