import os, json
from core.client import PagerDutyClient, getS3Client, get_athena_client
from core.config import in_dot_env_context, enrich_env_with_ssm_secrets
from core.writer import GoogleSheetsPagerDutyWriter
from core.service import PagerDutyService, GoogleSheetsService
from core.logging import get_logger
from core.response import get_response, get_lambda_proxy_response
from core.slack import auth_slack, get_events_director, slack_error_wrapper
import boto3
import slack
from datetime import datetime

@in_dot_env_context
@enrich_env_with_ssm_secrets([
    'SLACK_SIGNING_SECRET'
])
def auth_slack_event(event, context):
    logger = get_logger()

    if event == None:
        logger.info('No request body given. Aborting request')
        return get_lambda_proxy_response({"auth_ok": False, "reason": "Bad request"})

    slack_signature = event.get('headers', {}).get('X-Slack-Signature', '')
    slack_timestamp = event.get('headers', {}).get('X-Slack-Request-Timestamp', '')
    body = event.get('body', '{}')
    
    is_slack_auth_valid = auth_slack(os.getenv("SLACK_SIGNING_SECRET"), slack_timestamp, slack_signature, body)
    
    if not is_slack_auth_valid:
        logger.warn("Hash Mismatch for request given as: {0}".format(event))
        return get_lambda_proxy_response({"auth_ok": False, "reason": "Hash mismatch"})
    
    try:
        slack_event = json.loads(body)
    except:
        logger.warn("Json payload: load invalid" + str(body))
        return get_lambda_proxy_response({"auth_ok": False, "reason": "Bad request body"})
    
    #logger.info('Given slack payload: ' + str(slack_event))
    client = boto3.client('stepfunctions')
    try:
        result = client.start_execution(
            stateMachineArn = os.getenv('STEP_FUNCTION_ARN'),
            input = json.dumps(get_response("HANDLE_SLACK_EVENT", {'slack_event': slack_event}))
        )

        logger.info(f"Invokation started under arn: {result.get('executionArn','unknown')}")
    except Exception as e:
        logger.error(f'Invokation of step function failed! Reason: {repr(e)}')

    # handle challange response
    if slack_event.get('type', 'unknown') == 'url_verification':
        return get_lambda_proxy_response({"auth_ok": True, "challenge": slack_event.get("challenge", 'unknown')})
    
    return get_lambda_proxy_response({"auth_ok": True})
