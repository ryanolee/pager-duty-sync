class OnCallShift:
    def __init__(self, id, name, start_date, end_date):
        self.id=id
        self.name=name
        self.start_date=start_date
        self.end_date=end_date
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date,
            "end_date": self.end_date
        }
    
    def get_entity_file_name(self):
        return self.id + ".json"
    
    def __repr__(self):
        return "OnCallShift(if:{id}, name:{name}, start_date:{start_date}, end_date:{end_date})".format(**self.to_dict())

