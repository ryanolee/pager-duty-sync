import unittest
from core.client import PagerDutyClient

class TestPagerDutyService(unittest.TestCase):
    def setUp():
        self.client = PagerDutyClient(None)

    def test_is_shift_chargable_when_is_a_week_day(self):
    
        
if __name__ == "__main__":
    unittest.main()    