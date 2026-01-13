"""
Choice constants for loan models.

Ported from legacy cmtgdirect/loans/choices.py
"""

from localflavor.us.us_states import US_STATES, US_TERRITORIES

# State choices (US States + Territories)
STATE_CHOICES = US_STATES + US_TERRITORIES

# Boolean choices
NO = False
YES = True
YES_NO_CHOICES = (
    (YES, "Yes"),
    (NO, "No")
)

# Loan Purpose (max length: 12)
LOAN_PURPOSE_PURCHASE = 'purchase'
LOAN_PURPOSE_REFINANCE = 'refinance'
LOAN_PURPOSE_FIX_AND_FLIP = 'fix and flip'
LOAN_PURPOSE_RAW_LAND = 'raw land'
LOAN_PURPOSE_CONSTRUCTION = 'construction'
LOAN_PURPOSE_EQUITY_SHARE = 'equity share'
LOAN_PURPOSE_CHOICES = (
    (LOAN_PURPOSE_PURCHASE, "Purchase"),
    (LOAN_PURPOSE_REFINANCE, "Refinance"),
    (LOAN_PURPOSE_FIX_AND_FLIP, "Fix and Flip"),
    (LOAN_PURPOSE_RAW_LAND, "Raw Land"),
    (LOAN_PURPOSE_CONSTRUCTION, "Construction"),
    (LOAN_PURPOSE_EQUITY_SHARE, "Equity Share"),
)

# Property Type (max length: 15)
PROPERTY_TYPE_RESIDENTIAL = 'residential'
PROPERTY_TYPE_COMMERCIAL = 'commercial'
PROPERTY_TYPE_CHOICES = (
    (PROPERTY_TYPE_RESIDENTIAL, "Residential"),
    (PROPERTY_TYPE_COMMERCIAL, "Commercial"),
)

# Property Sub-Categories (max length: 25)
PROPERTY_TYPE_SUB_CATEGORY_SINGLE_FAMILY = 'single family'
PROPERTY_TYPE_SUB_CATEGORY_2_4_UNIT = '2-4 unit residential'
PROPERTY_TYPE_SUB_CATEGORY_CONDO_TOWNHOMES = 'condo townhomes'
PROPERTY_TYPE_SUB_CATEGORY_NON_WARRANTABLE_CONDO = 'non-warrantable condo'
PROPERTY_TYPE_SUB_CATEGORY_MANUFACTURED = 'manufactured'
PROPERTY_TYPE_SUB_CATEGORY_5_PLUS_UNITS = '5+ units'
PROPERTY_TYPE_SUB_CATEGORY_OFFICE = 'office'
PROPERTY_TYPE_SUB_CATEGORY_INDUSTRIAL = 'industrial'
PROPERTY_TYPE_SUB_CATEGORY_RETAIL = 'retail'
PROPERTY_TYPE_SUB_CATEGORY_HOSPITALITY = 'hospitality'
PROPERTY_TYPE_SUB_CATEGORY_SELF_STORAGE = 'self storage'
PROPERTY_TYPE_SUB_CATEGORY_MIXED_USE = 'mixed use'
PROPERTY_TYPE_SUB_CATEGORY_LAND = 'land'
PROPERTY_TYPE_SUB_CATEGORY_OTHER = 'other'

PROPERTY_TYPE_SUB_CATEGORY_CHOICES = (
    (PROPERTY_TYPE_SUB_CATEGORY_SINGLE_FAMILY, "Single-family residence"),
    (PROPERTY_TYPE_SUB_CATEGORY_2_4_UNIT, "2-4 unit residential"),
    (PROPERTY_TYPE_SUB_CATEGORY_CONDO_TOWNHOMES, "Condominiums and townhomes"),
    (PROPERTY_TYPE_SUB_CATEGORY_NON_WARRANTABLE_CONDO, "Non-warrantable condominiums"),
    (PROPERTY_TYPE_SUB_CATEGORY_MANUFACTURED, "Mobile/manufactured homes"),
    (PROPERTY_TYPE_SUB_CATEGORY_5_PLUS_UNITS, "5+ Units (Multi-family)"),
    (PROPERTY_TYPE_SUB_CATEGORY_OFFICE, "Office"),
    (PROPERTY_TYPE_SUB_CATEGORY_INDUSTRIAL, "Industrial"),
    (PROPERTY_TYPE_SUB_CATEGORY_RETAIL, "Retail"),
    (PROPERTY_TYPE_SUB_CATEGORY_HOSPITALITY, "Hospitality (hotels and motels)"),
    (PROPERTY_TYPE_SUB_CATEGORY_SELF_STORAGE, "Self-storage"),
    (PROPERTY_TYPE_SUB_CATEGORY_MIXED_USE, "Mixed-use"),
    (PROPERTY_TYPE_SUB_CATEGORY_LAND, "Land and/or lot"),
    (PROPERTY_TYPE_SUB_CATEGORY_OTHER, "Other"),
)

# Property Condition (max length: 2)
PROPERTY_CONDITION_C1 = 'C1'
PROPERTY_CONDITION_C2 = 'C2'
PROPERTY_CONDITION_C3 = 'C3'
PROPERTY_CONDITION_C4 = 'C4'
PROPERTY_CONDITION_C5 = 'C5'
PROPERTY_CONDITION_C6 = 'C6'
PROPERTY_CONDITION_CHOICES = (
    (PROPERTY_CONDITION_C1, "C1 - Excellent / New"),
    (PROPERTY_CONDITION_C2, "C2 - No Damage"),
    (PROPERTY_CONDITION_C3, "C3 - Little Damage"),
    (PROPERTY_CONDITION_C4, "C4 - Some Damage"),
    (PROPERTY_CONDITION_C5, "C5 - Obvious Damage"),
    (PROPERTY_CONDITION_C6, "C6 - Severe Damage"),
)

# Recourse Type (max length: 15)
FULL_RECOURSE = 'full recourse'
NON_RECOURSE = 'non-recourse'
RECOURSE_CHOICES = (
    (FULL_RECOURSE, "Full Recourse"),
    (NON_RECOURSE, "Non Recourse")
)

# Loan Type (max length: 15)
LOAN_TYPE_CONVENTIONAL = 'conventional'
LOAN_TYPE_ALT_A = 'Alt-A'
LOAN_TYPE_HARD_MONEY = 'hard money'
LOAN_TYPE_CONSTRUCTION = 'construction'
LOAN_TYPE_FIX_AND_FLIP = 'fix and flip'
LOAN_TYPE_CHOICES = (
    (LOAN_TYPE_CONVENTIONAL, "Conventional"),
    (LOAN_TYPE_ALT_A, "ALT A"),
    (LOAN_TYPE_HARD_MONEY, "Hard Money"),
    (LOAN_TYPE_CONSTRUCTION, "Construction"),
    (LOAN_TYPE_FIX_AND_FLIP, "Fix and Flip"),
)

# Lien Position (max length: 5)
MORTGAGE_NUMBER_1 = '1'
MORTGAGE_NUMBER_2 = '2'
MORTGAGE_NUMBER_3 = '3'
MORTGAGE_NUMBER_OTHER = 'other'
MORTGAGE_NUMBER_CHOICES = (
    (MORTGAGE_NUMBER_1, "1st Mortgage"),
    (MORTGAGE_NUMBER_2, "2nd Mortgage"),
    (MORTGAGE_NUMBER_3, "3rd Mortgage"),
    (MORTGAGE_NUMBER_OTHER, "Other"),
)

# Borrowing Entity Type (max length: 20)
BORROWING_ENTITY_TYPE_INDIVIDUAL = 'individual'
BORROWING_ENTITY_TYPE_NON_PROFIT = 'non-profit'
BORROWING_ENTITY_TYPE_C_CORPORATION = 'c-corp'
BORROWING_ENTITY_TYPE_S_CORPORATION = 's-corp'
BORROWING_ENTITY_TYPE_PARTNERSHIP = 'partnership'
BORROWING_ENTITY_TYPE_TRUST = 'trust'
BORROWING_ENTITY_TYPE_LLC = 'LLC'
BORROWING_ENTITY_TYPE_FOREIGN_NATIONAL = 'foreign national'
BORROWING_ENTITY_TYPE_FOREIGN_CORP = 'foreign corp'
BORROWING_ENTITY_TYPE_OTHER = 'other'
BORROWING_ENTITY_TYPE_CHOICES = (
    (BORROWING_ENTITY_TYPE_INDIVIDUAL, "Individual"),
    (BORROWING_ENTITY_TYPE_NON_PROFIT, "Non Profit"),
    (BORROWING_ENTITY_TYPE_C_CORPORATION, "C Corporation"),
    (BORROWING_ENTITY_TYPE_S_CORPORATION, "S Corporation"),
    (BORROWING_ENTITY_TYPE_PARTNERSHIP, "Partnership"),
    (BORROWING_ENTITY_TYPE_TRUST, "Trust"),
    (BORROWING_ENTITY_TYPE_LLC, "LLC"),
    (BORROWING_ENTITY_TYPE_FOREIGN_NATIONAL, "Foreign National"),
    (BORROWING_ENTITY_TYPE_FOREIGN_CORP, "Foreign Corp"),
    (BORROWING_ENTITY_TYPE_OTHER, "Other"),
)

# Occupancy Type (max length: 15)
OCCUPANCY_OWNER_OCCUPIED = 'owner occupied'
OCCUPANCY_SECOND_HOME = 'second home'
OCCUPANCY_INVESTMENT = 'investment'
OCCUPANCY_CHOICES = (
    (OCCUPANCY_OWNER_OCCUPIED, "Owner Occupied"),
    (OCCUPANCY_SECOND_HOME, "Second Home"),
    (OCCUPANCY_INVESTMENT, "Investment")
)

# Employment Type (max length: 10)
EMPLOYMENT_W2 = 'W2'
EMPLOYMENT_SELF = 'self'
EMPLOYMENT_FIXED = 'fixed'
EMPLOYMENT_CHOICES = (
    (EMPLOYMENT_W2, "W2 Wage Earner"),
    (EMPLOYMENT_SELF, "Self Employed"),
    (EMPLOYMENT_FIXED, "Fixed Income"),
)

# Income Documentation Type (max length: 30)
INCOME_TYPE_FULL = 'full'
INCOME_TYPE_STATED = 'stated'
INCOME_TYPE_CHOICES = (
    (INCOME_TYPE_FULL, "Full Income Documents (Taxes, Pay stubs)"),
    (INCOME_TYPE_STATED, "Stated (Low doc or no doc)"),
)

# Amortization Terms (max length: 20)
AMORTIZATION_TERM_1 = '1'
AMORTIZATION_TERM_5 = '5'
AMORTIZATION_TERM_10 = '10'
AMORTIZATION_TERM_20 = '20'
AMORTIZATION_TERM_25 = '25'
AMORTIZATION_TERM_30 = '30'
AMORTIZATION_TERM_40 = '40'
AMORTIZATION_TERM_5_1_ARM = '5/1'
AMORTIZATION_TERM_7_1_ARM = '7/1'
AMORTIZATION_TERM_CHOICES = (
    (AMORTIZATION_TERM_1, "1 Year"),
    (AMORTIZATION_TERM_5, "5 Years"),
    (AMORTIZATION_TERM_10, "10 Years"),
    (AMORTIZATION_TERM_20, "20 Years"),
    (AMORTIZATION_TERM_25, "25 Years"),
    (AMORTIZATION_TERM_30, "30 Years"),
    (AMORTIZATION_TERM_40, "40 Years"),
    (AMORTIZATION_TERM_5_1_ARM, "5/1 ARM"),
    (AMORTIZATION_TERM_7_1_ARM, "7/1 ARM"),
)

# Refinance Seasoning (max length: 5)
REFINANCE_SEASONING_0 = '0'
REFINANCE_SEASONING_6 = '6'
REFINANCE_SEASONING_12 = '12'
REFINANCE_SEASONING_24 = '24'
REFINANCE_SEASONING_CHOICES = (
    (REFINANCE_SEASONING_0, "0 Months (Immediate)"),
    (REFINANCE_SEASONING_6, "6 Months"),
    (REFINANCE_SEASONING_12, "12 Months"),
    (REFINANCE_SEASONING_24, "24 Months"),
)

# Prepayment Penalty (max length: 10)
PPP_NONE = 'none'
PPP_1_YEAR = '1 year'
PPP_2_YEAR = '2 year'
PPP_3_YEAR = '3 year'
PPP_5_YEAR = '5 year'
PPP_CHOICES = (
    (PPP_NONE, "None"),
    (PPP_1_YEAR, "1 Year"),
    (PPP_2_YEAR, "2 Years"),
    (PPP_3_YEAR, "3 Years"),
    (PPP_5_YEAR, "5 Years"),
)

# Prepayment Penalty Cost (max length: 4)
PPP_COST_1_PCT = '1'
PPP_COST_2_PCT = '2'
PPP_COST_3_PCT = '3'
PPP_COST_4_PCT = '4'
PPP_COST_5_PCT = '5'
PPP_COST_CHOICES = (
    (PPP_COST_1_PCT, "1%"),
    (PPP_COST_2_PCT, "2%"),
    (PPP_COST_3_PCT, "3%"),
    (PPP_COST_4_PCT, "4%"),
    (PPP_COST_5_PCT, "5%"),
)

# Rate Lock Terms (max length: 3)
RATE_LOCK_15_DAYS = '15'
RATE_LOCK_30_DAYS = '30'
RATE_LOCK_45_DAYS = '45'
RATE_LOCK_60_DAYS = '60'
RATE_LOCK_TERMS = (
    (RATE_LOCK_15_DAYS, "15 Days"),
    (RATE_LOCK_30_DAYS, "30 Days"),
    (RATE_LOCK_45_DAYS, "45 Days"),
    (RATE_LOCK_60_DAYS, "60 Days"),
)

# Lender Contact Type (max length: 25)
LENDER_CONTACT_TYPE_OWN = 'owner'
LENDER_CONTACT_TYPE_AE = 'account exec'
LENDER_CONTACT_TYPE_PROCESSOR = 'processor'
LENDER_CONTACT_TYPE_UNDERWRITER = 'underwriter'
LENDER_CONTACT_TYPE_CLOSER = 'closer'
LENDER_CONTACT_TYPE_CHOICES = (
    (LENDER_CONTACT_TYPE_OWN, "Owner"),
    (LENDER_CONTACT_TYPE_AE, "Account Executive"),
    (LENDER_CONTACT_TYPE_PROCESSOR, "Processor"),
    (LENDER_CONTACT_TYPE_UNDERWRITER, "Underwriter"),
    (LENDER_CONTACT_TYPE_CLOSER, "Closer"),
)
