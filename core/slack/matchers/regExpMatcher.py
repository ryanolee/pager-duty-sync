from .matcher import Matcher
import re 

class RegExpMatcher(Matcher):
    def __init__(self, event_type, regexes = []):
        super().__init__(event_type)
        self.regexes = [re.compile(regex) for regex in regexes]

    def match(self, event):
        return any([regex.search(event['text']) for regex in self.regexes])

    def __repr__(self):
        return f"<RegExpMatcher(event_type={self.event_type}, regexes={self.regexes})"