import os, json
from core.client import PagerDutyClient, getS3Client, get_athena_client
from core.config import in_dot_env_context, enrich_env_with_ssm_secrets
from core.writer import GoogleSheetsPagerDutyWriter
from core.service import PagerDutyService, GoogleSheetsService
from core.logging import get_logger
from core.response import get_response
from core.slack import auth_slack, get_events_director, handle_slack_error
import slack
from datetime import datetime

#@in_dot_env_context
#@enrich_env_with_ssm_secrets([
#    'SLACK_SIGNING_SECRET',
#    'SLACK_BOT_OAUTH_TOKEN'
#])
def handle_slack_event(event, context):
    return {}
    logger = get_logger()
    slack_signature = event.get('headers').get('X-Slack-Signature', '')
    slack_timestamp = event.get('headers').get('X-Slack-Request-Timestamp', '')
    body = event.get('body', '{}')
    
    logger.info('Supplied slack sginture:')
    
    is_slack_auth_valid = auth_slack(os.getenv("SLACK_SIGNING_SECRET"), slack_timestamp, slack_signature, body)
    
    if not is_slack_auth_valid:
        logger.warn("Hash Mismatch for request given as: {0}".format(event))
        return get_response(data={
            "message": "Hash mismatch!"
            }, success=False)
    
    try:
        slack_event = json.loads(body)
    except:
        logger.warn("Json payload: load invalid" + str(body))
        return get_response(False, {
            "message": "Json payload invalid"
        })
    
    
    event_type = slack_event.get('type', 'unknown')
    
    logger.info('Given slack payload: ' + str(slack_event))
    
    if event_type=='url_verification':
        return get_response(data={
            'challenge': slack_event.get('challenge', '')
        })
    
    client = None
    
    try:
        events_director = get_events_director()
        
        client = slack.WebClient(token=os.environ['SLACK_BOT_OAUTH_TOKEN'])
        
        events_director.handle_event(client, slack_event['event'])
    except Exception as e:
        handle_slack_error(client, e)
    return get_response(data={
        "message": "Request success!"
    })
    