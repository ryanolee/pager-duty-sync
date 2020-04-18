import requests
from .decorators import handle_errors_and_return_json

@handle_errors_and_return_json
def getBankHolidayData():
    return requests.get("https://www.gov.uk/bank-holidays.json")
    