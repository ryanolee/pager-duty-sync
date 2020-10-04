import os 
from core.logging import get_logger
from core.response import get_response
import traceback
import slack


def handle_slack_error(client, error):
    logger = get_logger()
    logger.error(str(error))
    
    user = {'ok': False}
    
    try:
        user = client.users_lookupByEmail(email = os.environ['SLACK_DEBUG_EMAIL'])
    except Exception as e:
        logger.error(f"Failed to send debug error message response: {user} error: {e}")
        return
    if not user['ok']:
        logger.warn(f"Failed to send debug error message as user could not be found: {user}")
        return 
    
    user_id = user['user']['id']
    post_message_response = {}
    error_message = "".join(traceback.TracebackException.from_exception(error).format())
    
    try:
        post_message_response = client.chat_postMessage(channel=user_id, text=f"Warning bot ran into an error: {error_message}")
    except Exception as e:
        logger.warn(f"Failed to send debug error message as could not send error: {e} message: {post_message_response}")
    
    return get_response("FATAL_ERROR_HIT", {"message": error_message})
"""
Wraps executions in error handle so that error messages for wrapped functions are forewarded through to slack
""" 
def slack_error_wrapper(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            client = slack.WebClient(token=os.environ['SLACK_BOT_OAUTH_TOKEN'])
            return handle_slack_error(client, e)

    return wrapper
