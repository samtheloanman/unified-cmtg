from rest_framework import serializers
from .models import (
    LoanApplication,
    Borrower,
    EmploymentEntry,
    AssetEntry,
    LiabilityEntry,
    Declarations
)

class EmploymentEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentEntry
        fields = '__all__'

class DeclarationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Declarations
        fields = '__all__'

class BorrowerSerializer(serializers.ModelSerializer):
    employments = EmploymentEntrySerializer(many=True, read_only=True)
    declarations = DeclarationsSerializer(read_only=True)

    class Meta:
        model = Borrower
        fields = '__all__'

class AssetEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetEntry
        fields = '__all__'

class LiabilityEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LiabilityEntry
        fields = '__all__'

class LoanApplicationSerializer(serializers.ModelSerializer):
    borrowers = BorrowerSerializer(many=True, read_only=True)
    assets = AssetEntrySerializer(many=True, read_only=True)
    liabilities = LiabilityEntrySerializer(many=True, read_only=True)

    class Meta:
        model = LoanApplication
        fields = '__all__'
