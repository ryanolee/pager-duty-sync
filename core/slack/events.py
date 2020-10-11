import re
from .eventDirector import EventDirector
from core.slack.permission import must_be_admin
from core.slack.matchers import RegExpMatcher, CallbackMatcher, is_app_home_event
from core.slack.util import get_all_users_from_blocks, get_all_user_profiles, get_date_range_from_string
from core.response import get_response
from datetime import datetime

event_director = EventDirector()

@event_director.on(matcher = RegExpMatcher('app_mention', ['help']))
def help_message(client, event):
    client.chat_postMessage(channel = event['channel'], blocks = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Hello there <@{event.get('user')}> :wave:!\n I am here to help you fill in the pager duty on call time sheet so you don't have to. Just ask me to 'fill in timesheets' for a particular period of time and I will get them over to you :chart_with_upwards_trend:. To find out more look [here](https://github.com/ryanolee/pager-duty-sync)!"
        }
    }])

    return get_response('EVENT_DONE')
    
@event_director.on(matcher = RegExpMatcher('app_mention', ['fill in timesheets']))
def fill_in_timesheets(client, event):
    # Get all users from post
    users = set([user.get('user_id') for user in get_all_users_from_blocks(event['blocks'])])

    # Do a lookup to get there profile data
    user_data = get_all_user_profiles(client, users)
    names = [user.get('real_name') for user in user_data.values()]
    
    # Try to guess the time range from the given string
    dates = get_date_range_from_string(event['text'])

    client.chat_postMessage(channel = event['channel'], blocks = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Sure! Will Have a look and get timesheets between {dates['start_date']} and {dates['end_date']} sent off to: {', '.join(names)} :chart_with_upwards_trend:"
        }
    }])
    
    #Get emails
    emails = [user.get('email') for user in user_data.values()]

    return get_response('FILL_IN_TIMESHEETS', {
        'emails': emails,
        'channel': event['channel'],
        **dates
    })

@event_director.on(matcher = RegExpMatcher('app_mention', ['sync to']))
@must_be_admin
def resync_to_s3(client, event):
    # Try to guess the time range from the given string
    dates = get_date_range_from_string(event['text'])

    client.chat_postMessage(channel = event['channel'], blocks = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Sure! Will resync pager duty records between {dates['start_date']} and {dates['end_date']}!"
        }
    }])

    return get_response('EXPORT_TO_S3', {
        'since': dates['start_date'],
        'until': dates['end_date'],
        'channel': event['channel']
    })

@event_director.on(matcher = CallbackMatcher('message', is_app_home_event))
@must_be_admin
def handle_admin_call(client, event):
    expression = re.compile("channel:\|(?P<channel>(?:.|\\\|)*)\|\s*message:\|(?P<message>(?:.|\\\|)*)\|")
    sender = event.get('user', None)

    result = expression.search(event.get('text'))

    if result == None:
        client.chat_postMessage(channel = sender, blocks = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Could not find expected response in given text (No message sent)"
            }
        }])
    
    else:
        client.chat_postMessage(channel = sender, blocks = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Posting event to channel: {result['channel']} with message: {result['message']}"
            }
        }])

        client.chat_postMessage(channel = result['channel'], blocks = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": result['message']
            }
        }])
    
    return get_response('EVENT_DONE')

def get_events_director():
    return event_director