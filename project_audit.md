# Project Audit Summary

## Overview
Audited `/custommortgage` (WordPress) and `/cmtgdirect` (Django) to validate migration gameplan.

---

## custommortgage (WordPress)

### Existing Assets
| Asset | Path | Reusable? |
|-------|------|-----------|
| ACF Field List | `PROGRAMS_ACF_FIELD_LIST.md` | ✅ Field mapping reference |
| Field Mapping | `FIELD_MAPPING_DETAILS.md` | ✅ Migration blueprint |
| ACF Export JSON | `programs-field-group-acf-export.json` | ✅ 92KB of field definitions |
| Agent Tools | `agent_tools.py` | ✅ Content extraction functions |
| WP Migrator | `wp_migrator.py` | ⚠️ Uses WP-CLI, not REST API |
| Page Extractor | `extract_pages.py` | ❌ SQL-based, not needed |
| llms.txt | `llms.txt` | ✅ Full site index |

### WordPress Content Structure (from ACF)
```
64 ACF Fields in 6 Tabs:
├── Location Tab (23 fields) - For local pages
├── Program Info Tab (8 fields) - Core data
├── Financial Terms Tab (7 fields) - Rates, LTV, etc.
├── Program Details Tab (7 fields) - Content blocks
├── Property & Loan Tab (8 fields) - Property types
└── Borrower Details Tab (4 fields) - Eligibility
```

---

## cmtgdirect (Django)

### Existing Assets
| Asset | Path | Reusable? |
|-------|------|-----------|
| LoanProgram Model | `loans/models/programs.py` | ✅ Already has most fields |
| API Views | `api/views.py` | ✅ QualifyView for pricing |
| Lender Model | `loans/models/programs.py` | ✅ Lender management |
| Floify Webhook | `api/views.py` | ⚠️ Placeholder only |
| Pages App | `pages/` | ❌ Minimal, not useful |

### LoanProgram Model Already Has
- name, lender, loan_type
- min_credit, potential_rate_min/max
- max_loan_amount, min_loan_amount
- max_ltv, min_dscr
- property_types, occupancy_types
- state restrictions

### Missing from Django (Need to Add)
- WYSIWYG content fields (details, FAQs, benefits)
- Local variation support (city/county data)
- Program highlights
- SEO fields (meta, slug, schema)

---

## Field Mapping: WP ACF → Django

| ACF Field | Django Field | Status |
|-----------|--------------|--------|
| name | name | ✅ Exists |
| program_type | loan_type | ✅ Similar |
| min_credit_score | min_credit | ✅ Exists |
| max_ltv | max_ltv | ✅ Exists |
| min_dscr | min_dscr | ✅ Exists |
| minimum_loan_amount | min_loan_amount | ✅ Exists |
| maximum_loan_amount | max_loan_amount | ✅ Exists |
| interest_rates | potential_rate_min/max | ✅ Similar |
| property_types_residential | property_types | ✅ Similar |
| occupancy | occupancy_types | ✅ Similar |
| --- Content Fields --- | | |
| details_about_mortgage_loan_program | - | ❌ Need TextField |
| requirements | - | ❌ Need TextField |
| mortgage_program_highlights | - | ❌ Need TextField |
| Program_FAQ | - | ❌ Need TextField |

---

## Gap Analysis

### ❌ Missing in Current Plan

1. **Content Fields Not in Django**
   - Django `LoanProgram` has structured data
   - WordPress has WYSIWYG rich content
   - **Fix**: Add content fields to Wagtail page model

2. **Local City Pages**
   - WP has 100+ local pages with city data
   - Django has no location model
   - **Fix**: Use MCP Census data for regeneration (Phase 2)

3. **SEO Metadata**
   - WP has Yoast SEO integration
   - Django has no SEO handling
   - **Fix**: Use Wagtail's built-in SEO

4. **Media Migration**
   - WP has wp-content/uploads (28K+ files)
   - Need to download and re-upload
   - **Fix**: Use WP REST media endpoint

### ✅ Already Solved

1. **Quote/Pricing Engine** - QualifyView exists
2. **Lender Management** - Lender model exists
3. **Floify Webhook** - Placeholder ready
4. **Docker** - Both projects have Docker setup

---

## Recommended Migration Approach

### Option A: Wagtail Pages (Recommended)
```
Wagtail ProgramPage (new)
├── Inherits from Wagtail Page
├── Fields: title, slug (built-in)
├── StreamField: content blocks
├── Related: LoanProgram (Django model for pricing)
└── SEO: Built into Wagtail
```

### Option B: Extend Django LoanProgram
```
LoanProgram model
├── Add content fields
├── Add SEO fields
├── Create template views
└── Custom admin
```

**Verdict**: Option A is cleaner. Wagtail handles content, Django handles pricing data.

---

## Updated Task Breakdown (Validated)

### Week 1: Extraction
- [x] WP REST API confirmed working
- [ ] Build extractor using `agent_tools.py` patterns
- [ ] Export programs, funded-loans, posts, locations
- [ ] Save as JSON with full ACF + Yoast data

### Week 2: Wagtail Setup
- [ ] Create Wagtail page models (ProgramPage, etc.)
- [ ] Map ACF content fields to StreamFields
- [ ] Import JSON data to Wagtail
- [ ] Verify URL slugs match

### Week 3: Integration
- [ ] Connect ProgramPage to LoanProgram (pricing data)
- [ ] Migrate QualifyView to new project
- [ ] Add chatbot widget

### Week 4: Deploy
- [ ] Deploy to cmre.c-mtg.com
- [ ] Verify all URLs work
- [ ] Set up redirects if needed

---

## Action Items Before Starting

1. ✅ Confirm WP REST API access
2. ⏳ Decide: Keep Django pricing data OR migrate to Wagtail?
3. ⏳ Clarify: What happens to existing cmtgdirect domain?
4. ⏳ Get: Floify webhook secret for production
