from .eventDirector import EventDirector
from core.slack.matchers import RegExpMatcher
from core.slack.util import get_all_users_from_blocks, get_all_user_profiles
from core import genarate_and_share_google_sheets

event_director = EventDirector()

@event_director.on(matcher = RegExpMatcher('app_mention', ['help']))
def post_help_message_to_channel(client, event):
    client.chat_postMessage(channel = event['channel'], blocks = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Hello there <@{event.get('user')}> :wave:!\nThere are many thinks I can do such as:\n* Fill in you timesheets \n* give you a dank meme :stonks:\n* probably some more stuff when ryan can be botherd to program it!"
        }
    }])
    
@event_director.on(matcher = RegExpMatcher('app_mention', ['fill in timesheets']))
def post_help_message_to_channel(client, event):
    # Get all users from post
    users = set([user.get('user_id') for user in get_all_users_from_blocks(event['blocks'])])
    # Do a lookup to get there profile data
    user_data = get_all_user_profiles(client, users)
    names = [user.get('real_name') for user in user_data.values()]
    
    client.chat_postMessage(channel = event['channel'], blocks = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Sure! Will Have a look and get timesheets sent off to: {','.join(names)} :+1:"
        }
    }])
    
    #Get emails
    emails = [user.get('email') for user in user_data.values()]

    genarate_and_share_google_sheets({"emails": emails}, None)
    
    client.chat_postMessage(channel = event['channel'], blocks = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"<@{event.get('user')}> Pager duty timesheets have been exported and sent!"
        }
    }])
    
    
    
def get_events_director():
    return event_director