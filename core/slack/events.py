from .eventDirector import EventDirector
from core.slack.matchers import RegExpMatcher
from core.slack.util import get_all_users_from_blocks, get_all_user_profiles, get_date_range_from_string
from core.response import get_response
from datetime import datetime
import calendar

event_director = EventDirector()

@event_director.on(matcher = RegExpMatcher('app_mention', ['help']))
def post_help_message_to_channel(client, event):
    client.chat_postMessage(channel = event['channel'], blocks = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Hello there <@{event.get('user')}> :wave:!\nThere are many things I can do such as:\n* Fill in you timesheets \n* give you a dank meme :stonks:\n* probably some more stuff when ryan can be botherd to program it!\n To find out more look here[here](https://github.com/ryanolee/pager-duty-sync)!"
        }
    }])
    
@event_director.on(matcher = RegExpMatcher('app_mention', ['fill in timesheets']))
def fill_in_timesheets(client, event):
    # Get all users from post
    users = set([user.get('user_id') for user in get_all_users_from_blocks(event['blocks'])])

    # Do a lookup to get there profile data
    user_data = get_all_user_profiles(client, users)
    names = [user.get('real_name') for user in user_data.values()]
    
    # Try to guess the time range from the given string
    dates = get_date_range_from_string(event['text'])

    # If not just give up assume the current month
    if dates == None:
        current_date = datetime.now()
        dates = {
            "start_date": datetime.today().replace(day=1),
            "end_date": current_date.replace(day=calendar.monthrange(current_date.year, current_date.month)[1])
        }

    # Convert dates into iso format (For further processing down the line, especially compatibility with athena)
    dates = {key: date.strftime("%Y-%m-%d") for (key, date) in dates.items()}

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
    
    
    
def get_events_director():
    return event_director