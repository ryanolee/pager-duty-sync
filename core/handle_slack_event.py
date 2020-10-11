import os, json
from core.client import PagerDutyClient, getS3Client, get_athena_client
from core.config import in_dot_env_context, enrich_env_with_ssm_secrets
from core.writer import GoogleSheetsPagerDutyWriter
from core.service import PagerDutyService, GoogleSheetsService
from core.logging import get_logger
from core.response import get_response
from core.slack import auth_slack, get_events_director, slack_error_wrapper
import slack
from datetime import datetime

@in_dot_env_context
@enrich_env_with_ssm_secrets([
    'SLACK_BOT_OAUTH_TOKEN'
])
# Remove until IM error loop detection is implemented
#@slack_error_wrapper
def handle_slack_event(event, context):
    events_director = get_events_director()

    # Try to get slack event from payload
    slack_event = event.get('PAYLOAD', {}).get('slack_event', {}).get('event', None)
    
    if slack_event == None:
        return get_response('NO_EVENT_SPECIFIED', {"message": "No event given for for the event director to direct."})

    client = slack.WebClient(token=os.environ['SLACK_BOT_OAUTH_TOKEN'])

    return events_director.handle_event(client, slack_event)
    