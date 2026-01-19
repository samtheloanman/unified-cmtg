from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from loans.models import Lender, LoanProgram, AddressInfo
from loans import choices

class QualifyViewTests(APITestCase):
    def setUp(self):
        # Create Lender
        self.lender = Lender.objects.create(
            company_name="Test Lender",
            include_states=["CA", "TX"],
        )
        
        # Create LoanProgram
        self.program = LoanProgram.objects.create(
            name="Test Program",
            lender=self.lender,
            min_loan_amount=100000,
            max_loan_amount=1000000,
            min_credit=600,
            max_loan_to_value=80.0,
            potential_rate_min=6.5,
            potential_rate_max=7.5,
            
            # ChoiceArrayFields
            property_types=[choices.PROPERTY_TYPE_RESIDENTIAL],
            purpose=[choices.LOAN_PURPOSE_PURCHASE],
            occupancy=[choices.OCCUPANCY_OWNER_OCCUPIED],
            
            # Required fields
            reserve_requirement=6,
            ysp_available=True,
            max_compensation=2,
            lender_fee=1000,
            prepayment_penalty=choices.PPP_NONE,
            prepayment_cost=choices.PPP_NONE,
            rate_lock_available=True,
            bk_allowed=True,
            foreclosure_allowed=True,
            short_sales_allowed=True,
            nod_allowed=True,
            nos_allowed=True,
            potential_cost_min=0,
            potential_cost_max=1,
            min_dscr=1.0, # Required by LoanProgram
        )

    def test_qualify_success(self):
        url = reverse('qualify')
        data = {
            "loan_amount": 200000,
            "property_value": 300000, # LTV = 66.66
            "loan_purpose": choices.LOAN_PURPOSE_PURCHASE,
            "property_type": choices.PROPERTY_TYPE_RESIDENTIAL,
            "property_state": "CA",
            "occupancy": choices.OCCUPANCY_OWNER_OCCUPIED,
            "credit_score": 700
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data
        self.assertEqual(results['total_matches'], 1)
        self.assertEqual(results['matched_programs'][0]['program_id'], self.program.id)
        self.assertEqual(results['calculated_ltv'], 66.67)

    def test_qualify_no_match_state(self):
        url = reverse('qualify')
        data = {
            "loan_amount": 200000,
            "property_value": 300000,
            "loan_purpose": choices.LOAN_PURPOSE_PURCHASE,
            "property_type": choices.PROPERTY_TYPE_RESIDENTIAL,
            "property_state": "NY", # Not in Lender states
            "occupancy": choices.OCCUPANCY_OWNER_OCCUPIED,
            "credit_score": 700
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_matches'], 0)

    def test_qualify_no_match_credit(self):
        url = reverse('qualify')
        data = {
            "loan_amount": 200000,
            "property_value": 300000,
            "loan_purpose": choices.LOAN_PURPOSE_PURCHASE,
            "property_type": choices.PROPERTY_TYPE_RESIDENTIAL,
            "property_state": "CA",
            "occupancy": choices.OCCUPANCY_OWNER_OCCUPIED,
            "credit_score": 550 # Below min_credit 600
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_matches'], 0)
