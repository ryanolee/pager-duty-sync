import os, json
from dateutil import parser
from core.client import PagerDutyClient, getS3Client, get_athena_client
from core.config import in_dot_env_context, enrich_env_with_ssm_secrets
from core.writer import GoogleSheetsPagerDutyWriter
from core.service import PagerDutyService, GoogleSheetsService
from core.logging import get_logger
from core.response import get_response
from core.slack import slack_error_wrapper
from datetime import datetime

@in_dot_env_context
@enrich_env_with_ssm_secrets([
    "ATHENA_USER_SECRET",
    "GOOGLE_SHEETS_SERVICE_USER_ACCOUNT_INFO",
    "SLACK_BOT_OAUTH_TOKEN"
])
@slack_error_wrapper
def generate_and_share_google_sheets(event, context):
    logger = get_logger()

    # Get payload from even
    payload = event.get("PAYLOAD")

    # In format yyyy-mm-dd
    date_from = payload.get('start_date')
    date_to = payload.get('end_date')

    # Get channel to send slack messages to when proxied
    slack_channel = payload.get('channel', False)

    # Parse datetimes
    date_from_dt = parser.isoparse(date_from)
    date_to_dt = parser.isoparse(date_to)

    time_difference = (date_to_dt - date_from_dt).days

    if time_difference > 180:
        return  get_response('SAY_TO_CHANNEL',{
            "message": f"Sorry I cannot really export more that 180 days at once. {time_difference} days between {date_from} and {date_to} is slightly too long :disappointed:",
            "channel": slack_channel
        })
    
    if time_difference <= 0:
        return get_response('SAY_TO_CHANNEL',{
            "message": f"Sorry I am a bit confused by when I need to export. Blame ryan and his rubbish NLP parsing :stinks:",
            "channel": slack_channel
        })

    share_emails = list(set([os.getenv('SLACK_DEBUG_EMAIL'), *payload.get('emails')]))

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
    
    return get_response('SAY_TO_CHANNEL',{
        "message": f"Timesheets have been exported from {date_from} to {date_to} with {len(cargeable_on_call_records)} items been exported in period :+1:",
        "channel": slack_channel
    })
