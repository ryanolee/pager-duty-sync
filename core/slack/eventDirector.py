from core.logging import get_logger

class EventDirector():
    def __init__(self):
        self.events = []

    """
    Allows user to register evets of certain types
    """
    def register_event(self, matcher, callback):
        self.events.append({
            'matcher': matcher,
            'callback': callback
        })
    
    """
    Handles event from slack API
    """
    def handle_event(self, client, event_payload):
        logger = get_logger()

        event_type = event_payload.get('type', 'unknown')
        for event in self.events:
            if event['matcher'].type_match(event_type) and event['matcher'].match(event_payload):
                logger.info(f"Directing recieved {event_type} with a payload of {event_payload} to {event['callback']}")
                return event['callback'](client, event_payload)
    
    """
    Wrapper for functions handling events from slack
    """
    def on(self, matcher):
        def matcher_wrapper(event_callback):
            self.register_event(matcher, event_callback)

            # Return the original event because we only want to register it (not overwite it)
            return event_callback
        return matcher_wrapper
    
    def __repr__(self):
        return f"<EventDirector(events={self.events})"
