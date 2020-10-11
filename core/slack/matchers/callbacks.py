
def is_app_home_event(event):
    return event.get('channel_type', 'unknown') == 'app_home'