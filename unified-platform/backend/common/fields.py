"""Custom Django model fields for the Unified CMTG Platform."""

from functools import partialmethod

from django import forms
from django.conf import settings
from django.forms.widgets import HiddenInput
from django.utils.encoding import force_str

# Check DB connection for SQLite vs PostgreSQL
if 'sqlite' in settings.DATABASES['default']['ENGINE']:
    from django.db.models import JSONField as ArrayField
else:
    from django.contrib.postgres.fields import ArrayField


class ArraySelectMultiple(forms.SelectMultiple):
    """Custom select widget for array fields."""

    def value_omitted_from_data(self, data, files, name):
        """Override to ensure empty arrays are handled correctly."""
        return False


class ChoiceArrayField(ArrayField):
    """
    An ArrayField that stores multiple choice values.

    Handles both PostgreSQL (using ArrayField) and SQLite (using JSONField).
    Provides automatic display methods for choice values.
    """

    def __init__(self, base_field=None, **kwargs):
        """Initialize the ChoiceArrayField."""
        if base_field is not None:
            self.base_field = base_field

        # Determine if we are using JSONField mock (SQLite)
        is_mocked = ArrayField.__name__ == 'JSONField'

        if is_mocked:
            # Strip arguments not supported by JSONField
            kwargs.pop('size', None)
            super().__init__(**kwargs)
        else:
            super().__init__(base_field, **kwargs)

    def db_type(self, connection):
        """Return database column type based on database backend."""
        if connection.vendor == 'sqlite':
            return 'text'
        return super().db_type(connection)

    def get_db_prep_value(self, value, connection, prepared=False):
        """Prepare value for database storage."""
        if connection.vendor == 'sqlite':
            import json
            if value is None:
                return None
            return json.dumps(value)
        return super().get_db_prep_value(value, connection, prepared)

    def formfield(self, **kwargs):
        """Return form field for admin interface."""
        defaults = {
            'form_class': forms.TypedMultipleChoiceField,
            'choices': self.base_field.choices,
            'coerce': self.base_field.to_python,
            'widget': ArraySelectMultiple
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)

    def to_python(self, value):
        """Convert database value to Python object."""
        res = super().to_python(value)
        if isinstance(res, list):
            value = [self.base_field.to_python(val) for val in res]
        return value

    @staticmethod
    def _get_display_values(model_instance, field):
        """Get human-readable display values for choices."""
        raw_values = getattr(model_instance, field.attname)
        values = []
        if raw_values:
            for value in raw_values:
                display = dict(field.base_field.flatchoices).get(value, value)
                values.append(force_str(display, strings_only=True))
        return values

    def contribute_to_class(self, cls, name, **kwargs):
        """Add custom display method to model class."""
        super().contribute_to_class(cls, name, **kwargs)
        setattr(
            cls,
            f'{self.name}_verbose',
            partialmethod(ChoiceArrayField._get_display_values, field=self)
        )
