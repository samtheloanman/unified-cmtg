from django.test import SimpleTestCase
from loans.services.matching import MatchingService
from decimal import Decimal
from collections import namedtuple

# Mock Program object
Program = namedtuple('Program', ['min_credit', 'max_loan_to_value', 'potential_rate_min', 'io_offered', 'ysp_available'])

class MatchingServiceTest(SimpleTestCase):
    def test_calculate_score_perfect_match(self):
        """Test a candidate with excellent metrics getting max score."""
        # Config: min_credit 600 (user 800 = +200 diff), max_ltv 90 (user 60 = +30 diff), rate 6.5 ( < 7 = +15)
        # Base 50 + 20 (credit) + 15 (ltv) + 15 (rate) = 100
        prog = Program(
            min_credit=600, 
            max_loan_to_value=Decimal('90.0'), 
            potential_rate_min=6.5, 
            io_offered=True, 
            ysp_available=True
        )
        data = {'credit_score': 800, 'calculated_ltv': 60.0}
        
        score = MatchingService.calculate_match_score(prog, data)
        self.assertEqual(score, 100)
    
    def test_calculate_score_bare_minimum(self):
        """Test a candidate that barely qualifies getting base score."""
        # Config: min_credit 600 (user 601 = +1 diff), max_ltv 80 (user 79 = +1 diff), rate 8.5 ( >= 8)
        # Base 50 + 0 + 0 + 0 = 50
        prog = Program(
            min_credit=600, 
            max_loan_to_value=Decimal('80.0'), 
            potential_rate_min=8.5, 
            io_offered=False, 
            ysp_available=False
        )
        data = {'credit_score': 601, 'calculated_ltv': 79.0}
        
        score = MatchingService.calculate_match_score(prog, data)
        self.assertEqual(score, 50)

    def test_get_program_notes(self):
        prog = Program(
            min_credit=600, max_loan_to_value=Decimal('90'), potential_rate_min=6, 
            io_offered=True, ysp_available=True
        )
        data = {'calculated_ltv': 85} # PMI warning trigger (>80)
        
        notes = MatchingService.get_program_notes(prog, data)
        self.assertIn("Interest-only payment option available", notes)
        self.assertIn("Lender-paid compensation available", notes)
        self.assertIn("May require mortgage insurance", notes)
