import requests
from .decorators import handle_errors_and_return_json

@handle_errors_and_return_json
def get_bank_holiday_data():
    return requests.get("https://www.gov.uk/bank-holidays.json")
    