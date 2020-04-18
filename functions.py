import os, json
from core.client import PagerDutyClient, getS3Client
from core.config import in_dot_env_context
from core.service import PagerDutyService

@in_dot_env_context
def export_pager_duty_reports_to_s3(event, context):
    # Load in env vars if files exsist in context


    # Load client
    client = PagerDutyClient( os.getenv("PAGER_DUTY_API_TOKEN") )
    schedule_id = os.getenv("PAGER_DUTY_SCHEDULE_ID")

    pager_duty_service = PagerDutyService(client)

    # Pull in pager duty service
    on_call_shifts = pager_duty_service.get_schedule_days_into_the_past(schedule_id, 7)

    s3 = getS3Client()
    
    for shift in on_call_shifts:
        print(shift)
        s3.write_on_call_entity(shift)

    #response = {
    #    "statusCode": 200,
    #    "body": json.dumps(body)
    #}

    #return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
