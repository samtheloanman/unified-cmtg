# Legacy Pricing Models Analysis (cmtgdirect)

**Track:** `port_pricing_ratesheet_20260112`
**Date:** 2026-01-13
**Agent:** The Generator

This document analyzes the core Django models from the legacy `cmtgdirect` application, which are essential for the pricing engine port. The primary source files are `legacy/cmtgdirect/loans/models/programs.py` and `legacy/cmtgdirect/loans/models/program_types.py`.

---

## 1. `Lender` Model

**File:** `legacy/cmtgdirect/loans/models/programs.py`

Represents a lending institution. This is the top-level object that owns loan programs and offerings.

### Fields

| Field | Type | Description |
|---|---|---|
| `company_name` | `CharField(max_length=500)` | The legal name of the lending company. |
| `include_states` | `ChoiceArrayField(USStateField)` | A list of US states where the lender is licensed to operate. |
| `company_website` | `URLField` | The lender's main website. |
| `company_phone` | `PhoneNumberField` | Main contact phone number. |
| `company_fax` | `PhoneNumberField` | Main contact fax number. |
| `company_email` | `EmailField` | General contact email. |
| `company_notes` | `TextField` | Internal notes about the lender. |

### Relationships

- Has a one-to-many relationship with `LoanProgram`.
- Has a one-to-many relationship with `LenderProgramOffering`.
- Has a one-to-many relationship with `LenderContact`.

---

## 2. `LoanProgram` Model

**File:** `legacy/cmtgdirect/loans/models/programs.py`

This is a large, detailed model that defines a specific loan product offered by a `Lender`. It inherits a significant number of fields from the abstract `BaseLoan` model.

### Inherited Fields from `BaseLoan` (Abstract)

This abstract model contains the majority of the eligibility criteria for a loan.

| Field | Type | Description |
|---|---|---|
| `name` | `CharField` | Name of the loan program. |
| `lender` | `ForeignKey('Lender')` | The lender offering this program. |
| `loan_type` | `CharField` | e.g., Conventional, FHA, VA. |
| `income_type` | `CharField` | e.g., Stated, Full Doc. |
| `occupancy` | `ChoiceArrayField` | e.g., Owner Occupied, Investment. |
| `property_types` | `ChoiceArrayField` | e.g., Residential, Commercial. |
| `property_sub_categories` | `ChoiceArrayField`| e.g., SFR, Condo, 2-4 Units. |
| `purpose` | `ChoiceArrayField` | e.g., Purchase, Refinance. |
| `min_loan_amount` | `DecimalField` | Minimum allowable loan amount. |
| `max_loan_amount` | `DecimalField` | Maximum allowable loan amount. |
| `max_loan_to_value`| `DecimalField` | Maximum LTV ratio. |
| `min_credit` | `PositiveSmallIntegerField` | Minimum FICO score. |
| `max_dti` | `PositiveIntegerField` | Maximum Debt-to-Income ratio. |
| `lender_fee` | `DecimalField` | The lender's underwriting/loan fee. |
| `prepayment_penalty` | `CharField` | Prepayment penalty options. |
| `bk_allowed` | `BooleanField` | Whether a past bankruptcy is allowed. |
| `time_since_bk` | `PositiveSmallIntegerField` | Required seasoning since bankruptcy. |
| `foreclosure_allowed`| `BooleanField` | Whether a past foreclosure is allowed. |
| `time_since_foreclosure` | `PositiveSmallIntegerField` | Required seasoning since foreclosure. |
| `...` | `...` | *Plus many other detailed eligibility fields.* |

### `LoanProgram` Specific Fields

| Field | Type | Description |
|---|---|---|
| `max_ltv_on_purchase_price` | `FloatField` | Max LTV based on the property's purchase price. |
| `max_ltv_on_arv` | `FloatField` | Max LTV based on After-Repair Value (for rehab loans). |
| `max_ltv_on_cost` | `FloatField` | Max Loan-to-Cost ratio. |
| `max_ltv_on_rehab` | `FloatField` | Max LTV on the rehab/construction funds. |
| `min_borrower_contribution` | `FloatField`| Minimum required cash contribution from the borrower. |
| `min_dscr` | `FloatField` | Minimum Debt Service Coverage Ratio. |

### Relationships

- `LoanProgram` has a direct `ForeignKey` to the `Lender` model. This creates a clear ownership structure where a `LoanProgram` belongs to exactly one `Lender`.

---

## 3. `LenderProgramOffering` Model

**File:** `legacy/cmtgdirect/loans/models/program_types.py`

This model acts as a bridge, connecting a generic `ProgramType` (e.g., "DSCR") with a specific `Lender`. It contains lender-specific pricing, fees, and requirement "overlays" that might be stricter than the base program type.

### Fields

| Field | Type | Description |
|---|---|---|
| `lender` | `ForeignKey('Lender')` | The lender providing this specific offering. |
| `program_type` | `ForeignKey('ProgramType')` | The canonical program type being offered. |
| `min_rate` | `FloatField` | Minimum interest rate for this offering. |
| `max_rate` | `FloatField` | Maximum interest rate for this offering. |
| `min_points` | `FloatField` | Minimum discount points. |
| `max_points` | `FloatField` | Maximum discount points. |
| `lender_fee` | `DecimalField` | The specific fee for this offering. |
| `min_fico` | `PositiveSmallIntegerField` | Lender's minimum FICO overlay. |
| `max_ltv` | `FloatField` | Lender's maximum LTV overlay. |
| `min_dscr` | `FloatField` | Lender's minimum DSCR overlay. |
| `min_loan` | `DecimalField` | Minimum loan amount for this offering. |
| `max_loan` | `DecimalField` | Maximum loan amount for this offering. |
| `rate_sheet_url` | `URLField` | Link to the lender's PDF rate sheet. |
| `last_rate_update`| `DateTimeField` | Timestamp of the last rate update. |
| `is_active` | `BooleanField` | Whether this offering is currently active. |
| `notes` | `TextField` | Internal notes. |

### Relationships

- **`unique_together = ['lender', 'program_type']`**: This is the core of the architecture. It ensures that a single lender can only have *one* offering for any given program type.
- This model connects the `Lender` with the `ProgramType`, acting as the central point for lender-specific data that isn't defined in the broader `LoanProgram` model.

---
## Summary & Handoff

The analysis reveals two distinct but related approaches to defining loan products in the legacy system:

1.  **`LoanProgram`**: A monolithic model where every detail and eligibility rule is a field. This is tied directly to a `Lender`.
2.  **`LenderProgramOffering`**: A more normalized approach, linking a `Lender` to a generic `ProgramType` and storing only the lender-specific *overrides* and *pricing*.

For the new `unified-platform`, the `LenderProgramOffering` architecture is the superior model to adopt. It is more scalable, easier to manage, and better separates canonical program rules from lender-specific pricing and overlays. The monolithic `LoanProgram` should be deprecated and its data migrated.

**Handoff to Ralph for verification.**
The next step is to verify that the analysis accurately reflects the models in the legacy codebase.
