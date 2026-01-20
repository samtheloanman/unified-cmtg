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


from cms.models import NavigationMenu, SiteConfiguration

class NavigationMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = NavigationMenu
        fields = ['id', 'name', 'translation_key', 'locale', 'raw_html']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        
        # If raw_html is present, we might skip items if frontend handles it, 
        # but let's send both just in case.
        
        # Custom streamfield serialization
        blocks = []
        for block in instance.items:
            # StructBlock values are dicts, already serializable usually
            # But Pages in PageChoosers need handling if present (LinkBlock has page chooser)
            
            val = block.value
            # For LinkBlock, handle page link
            if block.block_type == 'link':
                if val.get('link_page'):
                    # val['link_page'] is a Page object or ID depending on context, usually Page object in python
                    # We want the url
                    try:
                        val['link_url'] = val['link_page'].url
                    except:
                         val['link_url'] = None
                    # Remove the page object from dict to make it serializable
                    val.pop('link_page', None)

            elif block.block_type == 'sub_menu':
                # Similar logic for items inside
                sub_items = list(val.get('items', []))
                for sub_item in sub_items:
                    # sub_item is a LinkBlock value dict
                    if sub_item.get('link_page'):
                         try:
                             sub_item['link_url'] = sub_item['link_page'].url
                         except:
                             sub_item['link_url'] = None
                         sub_item.pop('link_page', None)
                # Overwrite with clean list
                val = dict(val)
                val['items'] = sub_items


            blocks.append({
                'type': block.block_type,
                'value': val,
                'id': getattr(block, 'id', None),
            })
        
        rep['items'] = blocks
        return rep


class SiteConfigurationSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SiteConfiguration
        fields = [
            'site_name', 'logo_url', 'phone_number', 'email', 'address',
            'facebook', 'twitter', 'linkedin', 'instagram',
            'translation_key', 'locale', 'footer_raw_html'
        ]

    def get_logo_url(self, obj):
        if obj.logo:
            return obj.logo.file.url
        return None

