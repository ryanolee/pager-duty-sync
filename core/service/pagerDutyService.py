from datetime import timezone, timedelta, datetime
from core.entitiy import OnCallShift

class PagerDutyService():
    def __init__(self, client):
        self.client = client

    """
    Handles retriving the schedule data for any given 
    """
    def get_schedule_days_into_the_past(self, schedule_id, days):
        until = datetime.now(timezone.utc)
        since = until - timedelta(days=days)

        result = self.client.get_schedule(schedule_id, since.isoformat(), until.isoformat())

        return [OnCallShift(
            scheduleEntry["id"],
            scheduleEntry["user"]["summary"], # Name in this context
            scheduleEntry["start"],
            scheduleEntry["end"]
        ) for scheduleEntry in result["schedule"]["final_schedule"]["rendered_schedule_entries"]]
    
    @classmethod
    def is_day_eligible(cls, onCallShift):
        pass


