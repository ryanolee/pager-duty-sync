from datetime import timezone, timedelta, datetime
from core.entitiy import OnCallShift
from core.client import get_bank_holiday_data
from core.util import DateTimeRange
from core.logging import get_logger
from dateutil import parser, rrule
from itertools import chain
from dateutil.rrule import rrule, HOURLY

class PagerDutyService():
    def __init__(self, client):
        self.client = client
        self.bank_holiday_data = None

    """
    Handles retriving the schedule data for any given 
    """
    def get_schedule_days_into_the_past(self, schedule_id, days):
        until = datetime.now(timezone.utc)
        since = until - timedelta(days=days)
        return self.get_time_range(schedule_id, since, until)

    def get_time_range(self, schedule_id, since, until):
        # Pager duty API seemingly accepts any time range so no need to exaust API ¯\_(ツ)_/¯
        result = self.client.get_schedule(schedule_id, since.isoformat(), until.isoformat())

        # Resolve last schedule entry
        final_schedule = result["schedule"]["final_schedule"]["rendered_schedule_entries"]

        # Chunk schedule into 12 hour incs in a flat format
        final_schedule_12h = []
        for shift in final_schedule:
            i = 0
            shift_end = parser.isoparse(shift['end'])
            for shift_start in rrule(
                freq=HOURLY,
                interval=12,
                dtstart=parser.isoparse(shift['start']),
                until=shift_end
            ):
                # Stop splitting shifts if we are going to be adding time that does not exsist
                if shift_start == shift_end:
                    break
                
                final_schedule_12h.append({
                    "id": shift["id"] + ("-{}".format(i) if i != 0 else ""),
                    "user": shift["user"]["summary"],
                    "start": shift_start,
                    "end": shift_start + timedelta(hours=12)
                })

                print(shift['id'], shift_start, shift_start + timedelta(hours=12))

                i+=1

        return [OnCallShift(
            scheduleEntry["id"],
            scheduleEntry["user"], # Name in this context
            scheduleEntry["start"],
            scheduleEntry["end"]
        ) for scheduleEntry in final_schedule_12h]
        
    """
    Works out if a on call shift is infact chargeable (this will only be the case when the shift is not during work hours)
    """
    def is_shift_chargable(self, on_call_shift):
        shift_range = on_call_shift.get_time_range()
        #the event midnight for the day the schedule ends is in the day mark it as eligible
        if shift_range.end.replace(hour=0, minute=0, second=0, microsecond=0) in shift_range:
            return True

        # In the event a scheduled day starts at the week end it should be chargeable
        if shift_range.start.weekday() >= 5:
            return True

        #Try to work out if a day is in bank holiday
        if self.bank_holiday_data == None:
            bank_holiday_data = get_bank_holiday_data()
            bank_holiday_date_time_objects = [datetime.strptime(bank_holiday["date"],'%Y-%m-%d') for bank_holiday in bank_holiday_data["england-and-wales"]["events"]]
            bank_holiday_ranges = [DateTimeRange(bank_holiday, bank_holiday + timedelta(days=1)) for bank_holiday in bank_holiday_date_time_objects]
            self.bank_holiday_data = bank_holiday_ranges 
        
        # Get if the shift matches any given bank holidays on record
        if any([shift_range.start in bank_holiday_range for bank_holiday_range in self.bank_holiday_data]):
            return True

        return False
