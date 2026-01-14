# Task: Restore LoanProgram Model (Critical Bug Fix)

**Priority**: 🚨 CRITICAL
**Assignee**: Claude (L2 Generator)
**Status**: Pending

## 🐛 The Bug
The project structure for `pricing` models was refactored to use a package (`pricing/models/`) containing multiple files (`programs.py`, `program_types.py`, etc.).

However, a file named `pricing/models.py` still exists. In Python/Django, the existence of `pricing/models.py` causes the `pricing/models/` package to be ignored (or shadowed) when doing `from pricing.models import ...`.

As a result, the `LoanProgram` model, which is defined in `pricing/models/programs.py` and exported in `pricing/models/__init__.py`, is **inaccessible**. This breaks `pricing/services/matching.py` and other components that depend on it.

## 🛠️ The Task
You need to fix this structural conflict to ensure the `LoanProgram` model is available.

### Steps:
1.  **Analyze**: Compare the contents of `unified-platform/backend/pricing/models.py` (the file) and `unified-platform/backend/pricing/models/` (the package).
2.  **Delete**: Delete the file `unified-platform/backend/pricing/models.py`.
3.  **Verify Package Exports**: Check `unified-platform/backend/pricing/models/__init__.py`. Ensure it correctly imports and exports all models:
    *   `Lender`
    *   `ProgramType`
    *   `LenderProgramOffering`
    *   `RateAdjustment`
    *   `LoanProgram` (Crucial!)
    *   `BaseLoan`
4.  **Verify Imports**: Ensure `unified-platform/backend/pricing/services/matching.py` can import `LoanProgram`.

## 🧪 Verification
Run this check in the Django shell (`python manage.py shell`):

```python
from pricing.models import LoanProgram, Lender, LenderProgramOffering
print(f"LoanProgram loaded: {LoanProgram}")
```

If this runs without `ImportError`, the fix is successful.
