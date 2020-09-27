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