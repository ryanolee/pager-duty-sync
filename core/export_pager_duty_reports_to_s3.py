import os, json, slack, pytz
from dateutil import parser
from core.client import PagerDutyClient, getS3Client, get_athena_client
from core.config import in_dot_env_context, enrich_env_with_ssm_secrets
from core.writer import GoogleSheetsPagerDutyWriter
from core.service import PagerDutyService, GoogleSheetsService
from core.logging import get_logger
from core.response import get_response
from core.slack import auth_slack, get_events_director, handle_slack_error
from datetime import datetime, timedelta

@in_dot_env_context
# This works out to be above free tier usage limits (Add in in other implementations)
@enrich_env_with_ssm_secrets([
    "PAGER_DUTY_API_TOKEN",
    "S3_USER_SECRET"
])
def export_pager_duty_reports_to_s3(event, context):
    payload = event.get("PAYLOAD", {})
    since = payload.get("since", None)
    until = payload.get("until", None)
    channel = payload.get("channel", None)

    since_dt = pytz.utc.localize(parser.isoparse(since) if since != None else (datetime.now() - timedelta(days=1)))
    until_dt = pytz.utc.localize(parser.isoparse(until) if until != None else datetime.now())

    if since_dt > until_dt:
        return get_response("BAD_ARGUMENTS", {
            "message": "The 'since' argument cannot be sooner than 'until'"
        })

    # Load logger 
    logger = get_logger()

    logger.info(f"Beginning sync process between pager duty and S3 from {since_dt.strftime('%b/%d/%Y')} to {until_dt.strftime('%b/%d/%Y')}")
    
    # Load client
    client = PagerDutyClient( os.getenv("PAGER_DUTY_API_TOKEN") )
    schedule_id = os.getenv("PAGER_DUTY_SCHEDULE_ID")

    pager_duty_service = PagerDutyService(client)
    
    # Pull in pager duty service
    on_call_shifts = pager_duty_service.get_time_range(schedule_id, since_dt, until_dt)
    
    # Hydrate if shifts are chargeable for any given entry
    on_call_shifts = [shift.with_is_chargeable(pager_duty_service.is_shift_chargable(shift)) for shift in on_call_shifts]
    on_call_shift_ids = [shift.id for shift in on_call_shifts]
    
    logger.info("Storing Pager Duty event ids into S3: {0}".format(', '.join(on_call_shift_ids)))
    
    s3 = getS3Client()
    
    for shift in on_call_shifts:
        s3.write_on_call_entity(shift)
        
    logger.info("Storing data finished.")

    # integration
    return get_response("SAY_TO_CHANNEL", {
        "message": f"Exported {len(on_call_shift_ids)} entitites to s3 :tada:",
        "channel": channel
    })