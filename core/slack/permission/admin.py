import os
from core.response import get_response

# Very basic auth layer for certain slack function to only allow certain users actions to functions
def is_user_admin(client, user_id):
    admin_emails = os.getenv('SLACK_ADMIN_EMAILS')

    if admin_emails == None:
        return False

    user = client.users_profile_get(user = user_id)
    
    return user.get('ok', False) and user.get('profile', {}).get('email') in admin_emails

def must_be_admin(func):
    def wrapped_func(client, evt):
        user_id = evt.get('user', None)
        if user_id == None or not is_user_admin(client, user_id):
            return get_response("SLACK_AUTHENTICATION_ERROR", {
                "message": f"User: {user_id} is not an admin in call to {func.__name__}. Aborting call"
            })
        
        return func(client, evt)
    
    return wrapped_func
            