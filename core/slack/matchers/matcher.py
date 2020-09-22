class Matcher():
    def __init__(self, event_type):
        self.event_type = event_type

    def type_match(self, event_type):
        return event_type == self.event_type