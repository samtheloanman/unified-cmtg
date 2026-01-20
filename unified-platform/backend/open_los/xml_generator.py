"""
Open Broker LOS - MISMO 3.4 XML Generator
Generates Fannie Mae compliant XML from LoanApplication models.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from django.utils import timezone
from .models import LoanApplication, Borrower, EmploymentEntry

class MismoXmlService:
    """
    Generates MISMO 3.4 XML structure.
    """
    
    @staticmethod
    def generate_xml(app: LoanApplication) -> str:
        """
        Main entry point. Returns pretty-printed XML string.
        """
        # Root Element
        message = ET.Element("MESSAGE", MiscObjectDescription="MISMO 3.4 Loan File")
        
        # Header (Standard wrapper)
        deal_sets = ET.SubElement(message, "DEAL_SETS")
        deal_set = ET.SubElement(deal_sets, "DEAL_SET")
        deals = ET.SubElement(deal_set, "DEALS")
        deal = ET.SubElement(deals, "DEAL")
        
        # 1. LOAN Information
        MismoXmlService._build_loan(deal, app)
        
        # 2. PARTIES (Borrowers)
        parties = ET.SubElement(deal, "PARTIES")
        for borrower in app.borrowers.all():
            MismoXmlService._build_party(parties, borrower)

        # 3. ASSETS (Dummy container if empty, strict validation might require it)
        if app.assets.exists():
            assets_container = ET.SubElement(deal, "ASSETS")
            for asset in app.assets.all():
                MismoXmlService._build_asset(assets_container, asset)

        # 4. LIABILITIES
        if app.liabilities.exists():
            liabs_container = ET.SubElement(deal, "LIABILITIES")
            for liab in app.liabilities.all():
                MismoXmlService._build_liability(liabs_container, liab)

        # Convert to string
        rough_string = ET.tostring(message, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    @staticmethod
    def _build_loan(parent, app: LoanApplication):
        """Constructs the LOAN segment."""
        loans = ET.SubElement(parent, "LOANS")
        loan = ET.SubElement(loans, "LOAN", LoanRoleType="SubjectLoan")
        
        terms = ET.SubElement(loan, "TERMS_OF_LOAN")
        ET.SubElement(terms, "LoanAmount").text = str(app.loan_amount)
        ET.SubElement(terms, "LoanPurposeType").text = app.loan_purpose or "Purchase"
        
        # Property
        collaterals = ET.SubElement(parent, "COLLATERALS")
        collateral = ET.SubElement(collaterals, "COLLATERAL")
        property_obj = ET.SubElement(collateral, "SUBJECT_PROPERTY")
        
        address = ET.SubElement(property_obj, "ADDRESS")
        ET.SubElement(address, "AddressLineText").text = app.property_address
        ET.SubElement(address, "StateCode").text = app.property_state

    @staticmethod
    def _build_party(parent, borrower: Borrower):
        """Constructs a PARTY segment validation."""
        party = ET.SubElement(parent, "PARTY")
        
        # Roles
        roles = ET.SubElement(party, "ROLES")
        role = ET.SubElement(roles, "ROLE")
        ET.SubElement(role, "ROLE_DETAIL", PartyRoleType="Borrower")
        
        borrower_detail = ET.SubElement(role, "BORROWER")
        ET.SubElement(borrower_detail, "BORROWER_DETAIL")
        
        # Employment
        if borrower.employments.exists():
             employers = ET.SubElement(borrower_detail, "EMPLOYERS")
             for emp in borrower.employments.all():
                 employer = ET.SubElement(employers, "EMPLOYER")
                 ET.SubElement(employer, "LegalEntityName").text = emp.employer_name
                 # Income would go here under CURRENT_INCOME_ITEMS
        
        # Individual
        individual = ET.SubElement(party, "INDIVIDUAL")
        name = ET.SubElement(individual, "NAME")
        ET.SubElement(name, "FirstName").text = borrower.first_name
        if borrower.middle_name:
            ET.SubElement(name, "MiddleName").text = borrower.middle_name
        ET.SubElement(name, "LastName").text = borrower.last_name
        if borrower.suffix:
            ET.SubElement(name, "SuffixName").text = borrower.suffix
        
        # Citizenship
        if borrower.citizenship:
            # Map simplified choices to MISMO Enums
            cit_map = {
                'citizen': 'USCitizen',
                'permanent_alien': 'PermanentResidentAlien',
                'non_permanent_alien': 'NonPermanentResidentAlien'
            }
            mismo_cit = cit_map.get(borrower.citizenship)
            if mismo_cit:
                ET.SubElement(individual, "CitizenshipResidencyType").text = mismo_cit
        
        contact = ET.SubElement(individual, "CONTACT_POINTS")
        if borrower.email:
            email = ET.SubElement(contact, "CONTACT_POINT")
            ET.SubElement(email, "ContactPointType").text = "Email"
            ET.SubElement(email, "ContactPointValue").text = borrower.email

    @staticmethod
    def _build_asset(parent, asset):
        asset_node = ET.SubElement(parent, "ASSET")
        detail = ET.SubElement(asset_node, "ASSET_DETAIL")
        ET.SubElement(detail, "AssetType").text = asset.account_type
        # MISMO format: Asset -> ASSET_HOLDER -> NAME
        ET.SubElement(detail, "AssetAccountIdentifier").text = asset.account_number_last4
        ET.SubElement(detail, "AssetCashOrMarketValueAmount").text = str(asset.cash_or_market_value)

    @staticmethod
    def _build_liability(parent, liab):
        l_node = ET.SubElement(parent, "LIABILITY")
        detail = ET.SubElement(l_node, "LIABILITY_DETAIL")
        ET.SubElement(detail, "LiabilityType").text = liab.liability_type
        ET.SubElement(detail, "LiabilityUnpaidBalanceAmount").text = str(liab.unpaid_balance)
        ET.SubElement(detail, "LiabilityMonthlyPaymentAmount").text = str(liab.monthly_payment)
