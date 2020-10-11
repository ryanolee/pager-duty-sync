from .matcher import Matcher
class CallbackMatcher(Matcher):
    def __init__(self, event_type, callback):
        super().__init__(event_type)
        self.callback = callback

    def match(self, *args, **kwags):
        return self.callback(*args, **kwags)
    
    def __repr__(self):
        return f"<CallbackMatcher(event_type={self.event_type}, callback={self.callback})"