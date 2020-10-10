import requests
from .decorators import handle_errors_and_return_json

class PagerDutyClient():
    def __init__(self, api_key):
        self.api_key = api_key

    @handle_errors_and_return_json
    def get_schedule(self, id, since, until):
        return requests.get(
            "{base_url}/schedules/{id}".format(
                base_url=self._get_base_url(),
                id=id
            ), 
            headers=self._get_auth_headers(),
            params = {
                "since": since,
                "until": until
            }
        )

    def _get_auth_headers(self):
        return  {
            'Accept': 'application/vnd.pagerduty+json;version=2',
            'Authorization': 'Token token={token}'.format(token=self.api_key)
        }
    
    def _get_base_url(self):
        return 'https://api.pagerduty.com'