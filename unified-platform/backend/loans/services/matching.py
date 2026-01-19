from decimal import Decimal

class MatchingService:
    @staticmethod
    def calculate_match_score(program, data):
        """
        Calculate a match score (0-100) based on borrower profile vs program constraints.
        """
        score = 50
        
        # Credit Score Buffer
        # data['credit_score'] is likely int. program.min_credit is int.
        credit_buffer = data['credit_score'] - program.min_credit
        if credit_buffer >= 100: score += 20
        elif credit_buffer >= 50: score += 10
        
        # LTV Buffer
        # data['calculated_ltv'] might be float or Decimal. program.max_loan_to_value is Decimal or float (check Model).
        # Model says Decimal. View says 'matches_found' uses float in some places?
        # Let's ensure Decimal comparison safely.
        try:
            ltv_val = Decimal(str(data['calculated_ltv']))
        except:
            ltv_val = Decimal(data['calculated_ltv'])
            
        ltv_buffer = program.max_loan_to_value - ltv_val
        if ltv_buffer >= 20: score += 15
        elif ltv_buffer >= 10: score += 10
        
        # Rate attractiveness
        if program.potential_rate_min < 7.0: score += 15
        elif program.potential_rate_min < 8.0: score += 10
        
        return min(score, 100)

    @staticmethod
    def get_program_notes(program, data):
        """
        Generate matching notes for the program.
        """
        notes = []
        if getattr(program, 'io_offered', False):
            notes.append("Interest-only payment option available")
        if getattr(program, 'ysp_available', False):
            notes.append("Lender-paid compensation available")
        
        # LTV Warning (PMI)
        try:
            ltv_val = float(data['calculated_ltv'])
        except:
            ltv_val = 0
            
        if ltv_val > 80:
            notes.append("May require mortgage insurance")
            
        return notes
