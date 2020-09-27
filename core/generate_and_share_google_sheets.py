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
