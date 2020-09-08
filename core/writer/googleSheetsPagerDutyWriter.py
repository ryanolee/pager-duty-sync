from io import StringIO
import csv

class GoogleSheetsPagerDutyWriter:
    _header_row = [
        "On Call",
        "Date from",
        "Date To",
        "DOW",
        "Support Call (PD Reference)",
        "Resolved / Escalated / NAR Ticket",
        "Time to resolve",
        "Assignees"
    ]
    
    def __init__(self, time_sheet_entries):
        self.time_sheet_entries = time_sheet_entries

    def add_time_entry(self, time_sheet_entry):
        self.time_sheet_entries.append(time_sheet_entry)

    def get_contents(self):
        #Remove not charageable results
        chargable_entries = filter(lambda timesheet_entry: timesheet_entry.is_chargeable, self.time_sheet_entries)
        
        output = StringIO()
        csv_writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        
        #Build csv file and output resulting values
        csv_writer.writerow(self._header_row)
        for entry in chargable_entries:
            csv_writer.writerow(entry.to_csv_row() + ["", "", "", ""])
        
        return output.getvalue()