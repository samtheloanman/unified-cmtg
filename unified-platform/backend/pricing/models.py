"""
Pricing models - backward compatibility wrapper.

This file maintains backward compatibility for any existing imports
of `from pricing.models import ...`

All models are now organized in the pricing/models/ package.
"""

# Import all models from the package
from pricing.models import *  # noqa: F401, F403
