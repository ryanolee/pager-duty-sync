from pytz import timezone

class DateTimeRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end
    
    def __contains__(self, time):
        # Normalise timezones to UTC for comparisons so we always 
        utc_timezone = timezone("UTC")
        return self.start.astimezone(utc_timezone) < time.astimezone(utc_timezone)  <= self.end.astimezone(utc_timezone) 