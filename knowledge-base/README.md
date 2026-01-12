# Knowledge Base

> **Purpose**: Reference documentation for AI agents and developers working on the Unified CMTG Platform.

---

## 📂 Contents

### Active Documentation

| File | Description |
|------|-------------|
| [rate_extraction_field_mapping.md](./rate_extraction_field_mapping.md) | Mapping of rate sheet fields to Django models |
| [ratesheet_extraction_sop.md](./ratesheet_extraction_sop.md) | Standard Operating Procedure for rate sheet extraction |

### Archived Documentation

| File | Description |
|------|-------------|
| [archive-v1/prd.md](./archive-v1/prd.md) | Original v1 PRD (superseded by v2) |
| [archive-v1/prd_simplified.md](./archive-v1/prd_simplified.md) | Simplified v1 PRD |
| [archive-v1/implementation_plan.md](./archive-v1/implementation_plan.md) | Original implementation plan |
| [archive-v1/project_audit.md](./archive-v1/project_audit.md) | Initial project audit |
| [archive-v1/project_review.md](./archive-v1/project_review.md) | Detailed project review |

---

## 🔑 Key Concepts

### Rate Sheet Structure

Rate sheets from wholesale lenders typically contain:
1. **Base Rate Matrix**: Rates vs. prices by lock period
2. **LLPA Grids**: FICO × LTV adjustments
3. **Other Adjustments**: Property type, occupancy, purpose, etc.

### Quote Calculation

```
Final Price = Base Price + Sum(LLPA Adjustments)
Cost to Borrower = (100 - Final Price) × Loan Amount
```

### Field Mapping

The `rate_extraction_field_mapping.md` document defines how extracted data maps to:
- `LenderProgramOffering` model fields
- `RateAdjustment` model fields

---

## 📖 Usage

These documents are consumed by:
1. **Rate Sheet Agent**: Uses SOPs to guide extraction
2. **Pricing Engineer**: Uses field mappings for model design
3. **Human Reviewers**: Uses SOPs to validate extracted data

---

*Last Updated: 2026-01-11*
