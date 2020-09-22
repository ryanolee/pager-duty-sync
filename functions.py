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


@in_dot_env_context
# This works out to be above free tier usage limits (Add in in other implementations)
@enrich_env_with_ssm_secrets([
    "PAGER_DUTY_API_TOKEN",
    "S3_USER_SECRET"
])
def export_pager_duty_reports_to_s3(event, context):
    
    return {}
    
    # Load logger 
    logger = get_logger()

    logger.info("Beginning sync process between S3 and ")
    
    # Load client
    client = PagerDutyClient( os.getenv("PAGER_DUTY_API_TOKEN") )
    schedule_id = os.getenv("PAGER_DUTY_SCHEDULE_ID")

    pager_duty_service = PagerDutyService(client)
    
    # Pull in pager duty service
    on_call_shifts = pager_duty_service.get_schedule_days_into_the_past(schedule_id, 30)
    
    # Hydrate if shifts are chargeable for any given entry
    on_call_shifts = [shift.with_is_chargeable(pager_duty_service.is_shift_chargable(shift)) for shift in on_call_shifts]
    on_call_shift_ids = [shift.id for shift in on_call_shifts]
    
    logger.info("Storing Pager Duty event ids into S3: {0}".format(', '.join(on_call_shift_ids)))
    
    s3 = getS3Client()
    
    for shift in on_call_shifts:
        s3.write_on_call_entity(shift)
        
    logger.info("Storing data finished.")

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    return get_response(data={
        "exported_shift_ids": on_call_shift_ids
    })

@in_dot_env_context
@enrich_env_with_ssm_secrets([
    "ATHENA_USER_SECRET",
    "GOOGLE_SHEETS_SERVICE_USER_ACCOUNT_INFO"
])
def genarate_and_share_google_sheets(event, context):
    logger = get_logger()
    
    date_from = "2020-01-01"
    date_to = "2020-10-01"
    share_emails = ["landgraabiv@gmail.com"]

    
    logger.info("Beginning google sheet creation for timesheets from {0} to {1} for users:{2}".format(date_from, date_to, ','.join(share_emails)))
    
    athena_client = get_athena_client()
    cargeable_on_call_records = athena_client.get_chargeable_on_call_data(date_from, date_to)
    logger.info("Found {0} rows to sync to google sheets".format(len(cargeable_on_call_records)))
    
    now = datetime.now()
    pager_duty_title = "PagerDuty on call timesheet {0} - {1} generated on {2}".format(date_from, date_to, now.strftime("%d/%m/%Y %H:%M:%S"))
    
    google_sheets_creds = json.loads(os.getenv("GOOGLE_SHEETS_SERVICE_USER_ACCOUNT_INFO"))
    service = GoogleSheetsService(google_sheets_creds)
    writer = GoogleSheetsPagerDutyWriter(cargeable_on_call_records)
    
    service.saveWriterContents(pager_duty_title, writer)
    service.share_sheet_by_title(pager_duty_title, share_emails)
    
    logger.info("Generated google sheet: '{0}' and shared with '{1}'".format(pager_duty_title, "', '".join(share_emails)))
    
    return get_response(data={
        "success": true,
        "message": "Generated google sheet: '{0}' and shared with {1} users".format(pager_duty_title, len(share_emails))
    })

@in_dot_env_context
@enrich_env_with_ssm_secrets([
    'SLACK_SIGNING_SECRET',
    'SLACK_BOT_OAUTH_TOKEN'
])
def handle_slack_event(event, context):
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
    