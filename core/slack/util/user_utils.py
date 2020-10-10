import os

def get_all_user_profiles(client, user_ids, remove_bots = True):
    profile_data = {}

    for user_id in user_ids:
        user = client.users_profile_get(user = user_id)
        if not user.get('ok', False):
            continue
        
        if remove_bots and 'bot_id' in user.get('profile', {}):
            continue
        
        profile_data[user_id] = user.get('profile', {})

    return profile_data
