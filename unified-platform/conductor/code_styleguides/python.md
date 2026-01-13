# Python Style Guide - Unified CMTG Platform

This document defines Python conventions for the Unified CMTG Platform, built on Google Python Style Guide with Django/DRF-specific patterns.

## 1. Foundational Rules (Google Style Guide)

### 1.1 Language Rules
- **Linting:** Run `pylint`, `flake8`, and `mypy` on all code.
- **Imports:** Use `import x` for packages/modules. Use `from x import y` for functions/classes. Group: stdlib → third-party → local.
- **Exceptions:** Use specific exception classes, never bare `except:` clauses.
- **Global State:** Avoid mutable globals. Module constants should be `ALL_CAPS_WITH_UNDERSCORES`.
- **Type Annotations:** Strongly encouraged for all public APIs, especially Django models and DRF serializers.
- **Mutable Defaults:** Never use `[]` or `{}` as default argument values. Use `None` instead.
- **None Checks:** Use `if foo is None:` (not `if not foo:` for None checks).

### 1.2 Formatting
- **Line Length:** Maximum 88 characters (Black formatter default).
- **Indentation:** 4 spaces, never tabs.
- **Blank Lines:** 2 between module-level definitions, 1 between methods.
- **Docstrings:** Use `"""triple double quotes"""`. All public modules, classes, functions, methods must have docstrings.
  - Format: One-line summary, blank line, detailed description (if needed), then `Args:`, `Returns:`, `Raises:` sections.

### 1.3 Naming
- **Modules/Functions/Variables:** `snake_case`
- **Classes/Exceptions:** `PascalCase`
- **Constants:** `ALL_CAPS_WITH_UNDERSCORES`
- **Private:** Single leading underscore `_private_var` (internal module/class use only)
- **Never use:** Double leading underscores for name mangling

---

## 2. Django Model Patterns

### 2.1 Model Definition
```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from wagtail.models import Page
from modelcluster.fields import ParentalKey

class LoanProgram(Page):
    """A loan program offered by a lender."""

    lender = models.ForeignKey(
        'pricing.Lender',
        on_delete=models.CASCADE,
        related_name='loan_programs',
        help_text="The lender offering this program"
    )
    min_credit_score = models.IntegerField(
        default=620,
        validators=[MinValueValidator(300), MaxValueValidator(850)],
    )
    max_ltv = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=80.0,
    )

    class Meta:
        verbose_name = "Loan Program"
        verbose_name_plural = "Loan Programs"
        ordering = ['lender', 'name']
        indexes = [
            models.Index(fields=['lender', 'name']),
        ]

    def __str__(self) -> str:
        return f"{self.lender.name} - {self.name}"
```

### 2.2 Model Patterns
- **Ordering:** Meta fields, then ForeignKey/ManyToMany relations, then regular fields
- **Help Text:** Add to all fields for admin clarity
- **Meta.indexes:** Define for frequently queried field combinations
- **Validators:** Use built-in validators (MinValueValidator, MaxValueValidator, URLValidator)
- **QuerySet Methods:** Use `Manager` for custom querysets

### 2.3 Custom Managers
```python
class LenderQuerySet(models.QuerySet):
    def active(self):
        """Return only active lenders."""
        return self.filter(is_active=True)

    def by_state(self, state: str):
        """Filter lenders operating in given state."""
        return self.filter(states__contains=[state])

class LenderManager(models.Manager):
    def get_queryset(self):
        return LenderQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

class Lender(models.Model):
    objects = LenderManager()
```

---

## 3. Django REST Framework (DRF) Patterns

### 3.1 Serializers
```python
from rest_framework import serializers
from .models import LoanProgram, Lender

class LenderSerializer(serializers.ModelSerializer):
    """Serializer for Lender model."""

    class Meta:
        model = Lender
        fields = ['id', 'name', 'nmls_id', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class LoanProgramSerializer(serializers.ModelSerializer):
    """Serializer for LoanProgram with nested lender."""

    lender = LenderSerializer(read_only=True)
    lender_id = serializers.PrimaryKeyRelatedField(
        queryset=Lender.objects.all(),
        write_only=True,
    )

    class Meta:
        model = LoanProgram
        fields = [
            'id', 'lender', 'lender_id', 'name', 'min_credit_score',
            'max_ltv', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
```

### 3.2 ViewSets
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

class LoanProgramViewSet(viewsets.ModelViewSet):
    """ViewSet for loan programs."""

    queryset = LoanProgram.objects.all().select_related('lender')
    serializer_class = LoanProgramSerializer
    filterset_fields = ['lender', 'min_credit_score']
    search_fields = ['name', 'lender__name']
    ordering_fields = ['name', 'min_credit_score']
    ordering = ['name']

    @action(detail=False, methods=['post'])
    def qualify(self, request):
        """Qualify based on loan criteria."""
        serializer = QualifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        matching_programs = self.queryset.filter(
            min_credit_score__lte=serializer.validated_data['credit_score'],
            max_ltv__gte=serializer.validated_data['ltv'],
        )

        return Response(
            LoanProgramSerializer(matching_programs, many=True).data,
            status=status.HTTP_200_OK
        )
```

---

## 4. Service Layer (Business Logic)

### 4.1 Service Pattern
```python
# pricing/services.py
from typing import List
from decimal import Decimal

class PricingService:
    """Service for pricing calculations."""

    @staticmethod
    def calculate_rate(
        program: LoanProgram,
        credit_score: int,
        ltv: Decimal,
    ) -> Decimal:
        """
        Calculate interest rate for given program and borrower profile.

        Args:
            program: LoanProgram instance
            credit_score: Borrower FICO score (300-850)
            ltv: Loan-to-value ratio (0-100)

        Returns:
            Interest rate as Decimal

        Raises:
            ValueError: If parameters are invalid
        """
        if not 300 <= credit_score <= 850:
            raise ValueError(f"Invalid credit score: {credit_score}")

        base_rate = program.base_rate
        # Apply adjustments...
        return base_rate
```

---

## 5. Testing Patterns

### 5.1 Test Structure
```python
# pricing/tests/test_models.py
from django.test import TestCase
from pricing.models import Lender, LoanProgram

class LenderModelTests(TestCase):
    """Tests for Lender model."""

    def setUp(self):
        """Set up test fixtures."""
        self.lender = Lender.objects.create(
            name="Test Bank",
            nmls_id="123456",
        )

    def test_lender_str_representation(self):
        """Test __str__ method."""
        self.assertEqual(str(self.lender), "Test Bank")

    def test_loan_program_creation(self):
        """Test creating a loan program."""
        program = LoanProgram.objects.create(
            lender=self.lender,
            name="30-Year Fixed",
            min_credit_score=680,
        )
        self.assertEqual(program.lender, self.lender)
```

### 5.2 API Tests
```python
# api/tests/test_views.py
from rest_framework.test import APITestCase
from rest_framework import status

class LoanProgramAPITests(APITestCase):
    """Tests for LoanProgram API endpoints."""

    def setUp(self):
        self.lender = Lender.objects.create(name="Test Bank")
        self.program = LoanProgram.objects.create(
            lender=self.lender,
            name="30-Year Fixed",
        )

    def test_list_loan_programs(self):
        """Test listing loan programs."""
        response = self.client.get('/api/v1/loan-programs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

---

## 6. Celery Task Patterns

### 6.1 Celery Tasks
```python
# pricing/tasks.py
from celery import shared_task
from .models import RateSheet

@shared_task(bind=True, max_retries=3)
def ingest_rate_sheet(self, rate_sheet_id: int) -> dict:
    """
    Ingest a rate sheet PDF and extract rates.

    Args:
        rate_sheet_id: ID of RateSheet instance

    Returns:
        Dictionary with extraction results
    """
    try:
        rate_sheet = RateSheet.objects.get(id=rate_sheet_id)
        # Process...
        return {'status': 'success', 'extracted_rows': 50}
    except RateSheet.DoesNotExist:
        raise ValueError(f"RateSheet {rate_sheet_id} not found")
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

---

## 7. Code Quality Tools

### 7.1 Configuration Files

**pyproject.toml** (Black, pytest):
```ini
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  migrations
  | __pycache__
  | \.git
)/
'''

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
addopts = "--cov=. --cov-report=html --cov-fail-under=80"
```

**setup.cfg** (flake8, coverage):
```ini
[flake8]
max-line-length = 88
exclude = .git,__pycache__,migrations
ignore = E203,W503

[coverage:run]
source = .
omit = */migrations/*,*/tests/*,manage.py
```

### 7.2 Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        args: [--ignore-missing-imports]
        additional_dependencies: [djangorestframework, wagtail]
```

---

## 8. Import Organization

```python
# Standard library
import os
import sys
from pathlib import Path
from typing import List, Optional

# Third-party
import django
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from wagtail.models import Page

# Local
from pricing.models import Lender
from pricing.services import PricingService
```

---

## 9. Be Consistent

When editing existing code, match the surrounding style. Consistency trumps these guidelines when conflict arises.

---

*Last Updated: 2026-01-12*
*Based on: [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)*