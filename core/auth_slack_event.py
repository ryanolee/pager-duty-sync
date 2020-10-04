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
    'SLACK_SIGNING_SECRET'
])
@slack_error_wrapper
def auth_slack_event(event, context):
    logger = get_logger()

    if event == None:
        logger.info('No request body given. Aborting request')
        return get_response("AUTH_FAILED", {'reason': 'Bad Request'})

    slack_signature = event.get('headers', {}).get('X-Slack-Signature', '')
    slack_timestamp = event.get('headers', {}).get('X-Slack-Request-Timestamp', '')
    body = event.get('body', '{}')
    
    is_slack_auth_valid = auth_slack(os.getenv("SLACK_SIGNING_SECRET"), slack_timestamp, slack_signature, body)
    
    if not is_slack_auth_valid:
        logger.warn("Hash Mismatch for request given as: {0}".format(event))
        return get_response("AUTH_FAILED", {'reason': 'Hash Mismatch'})
    
    try:
        slack_event = json.loads(body)
    except:
        logger.warn("Json payload: load invalid" + str(body))
        return get_response("AUTH_FAILED", {'reason': 'Payload invalid'})
    
    #logger.info('Given slack payload: ' + str(slack_event))
    
    return get_response("AUTH_PASSED", {'slack_event': slack_event})
