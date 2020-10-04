import slack, os
from core.response import get_response
from core.config import in_dot_env_context, enrich_env_with_ssm_secrets
from core.slack import slack_error_wrapper
from core.logging import get_logger

@in_dot_env_context
@enrich_env_with_ssm_secrets([
    'SLACK_BOT_OAUTH_TOKEN'
])
@slack_error_wrapper
def send_message_to_channel(event, context):
    payload = event.get("PAYLOAD", {})

    message = payload.get('message', None)
    channel = payload.get('channel', None)

    if message == None or channel == None:
        return get_response("BAD_STATE", {
            "message": "Bad payload given."
        })
    
    client = slack.WebClient(token=os.environ['SLACK_BOT_OAUTH_TOKEN'])
    logger = get_logger()

    client.chat_postMessage(channel = channel, blocks = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": message
        }
    }])

    logger.info(f"Sent message to channel: {message}")

    return get_response("WORKFLOW_FINISHED")
    