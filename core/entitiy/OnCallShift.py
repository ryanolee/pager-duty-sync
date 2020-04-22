from core.util import DateTimeRange
from dateutil import parser

class OnCallShift:
    def __init__(self, id, name, start_date, end_date, is_chargeable = False):
        self.id=id
        self.name=name
        self.start_date=start_date
        self.end_date=end_date
        self.is_chargeable = is_chargeable
    
    def with_is_chargeable(self, is_chargeable):
        self.is_chargeable = is_chargeable
        return self

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            #Convert date times to unix format for athena support
            "start_date": parser.isoparse(self.start_date).strftime("%Y-%m-%d %H:%M:%S"),
            "end_date": parser.isoparse(self.end_date).strftime("%Y-%m-%d %H:%M:%S"),
            "is_chargeable": self.is_chargeable
        }

    def get_entity_file_name(self):
        return self.id + ".json"
    
    def __repr__(self):
        return "OnCallShift(if:{id}, name:{name}, start_date:{start_date}, end_date:{end_date}, is_chargeable:{is_chargeable})".format(**self.to_dict())
    
    """
    Gets a time range object representing the start to end times of a given on call shift
    """
    def get_time_range(self):
        return DateTimeRange(parser.isoparse(self.start_date), parser.isoparse(self.end_date))

