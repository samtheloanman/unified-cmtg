from django.test import TestCase
from cms.models import Office

class OfficeModelTest(TestCase):
    def setUp(self):
        self.hq = Office.objects.create(
            name="HQ",
            city="Encino",
            state="CA",
            latitude=34.154500,
            longitude=-118.495300,
            is_headquarters=True,
            is_active=True
        )
        self.branch = Office.objects.create(
            name="Branch",
            city="San Diego",
            state="CA",
            latitude=32.715700,
            longitude=-117.161100,
            is_headquarters=False,
            is_active=True
        )
        self.closed = Office.objects.create(
            name="Closed",
            city="Nowhere",
            state="ZZ",
            latitude=0,
            longitude=0,
            is_headquarters=False,
            is_active=False
        )

    def test_office_creation(self):
        self.assertEqual(Office.objects.count(), 3)
        self.assertEqual(str(self.hq), "HQ - Encino, CA")

    def test_manager_active(self):
        active_offices = Office.objects.active()
        self.assertEqual(active_offices.count(), 2)
        self.assertIn(self.hq, active_offices)
        self.assertIn(self.branch, active_offices)
        self.assertNotIn(self.closed, active_offices)

    def test_manager_headquarters(self):
        hq = Office.objects.headquarters()
        self.assertEqual(hq, self.hq)
