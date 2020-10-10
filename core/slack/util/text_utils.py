from dateparser.search import search_dates
from datetime import datetime
import calendar

def get_all_users_from_blocks(blocks, users = []):
    for block in blocks:
        if block.get('type', 'unknown') == 'user':
            users.append(block)
        
        if block.get('elements', None) != None:
            users = get_all_users_from_blocks(block['elements'], users)

    return users

"""
Gets date range based on message text using some very basic NLP
Ideally would use heideltime but could not get proper runtime ENV setup in lambda

Assumptions: 
 - Tokens will be assumed to be a range from ... to ... if two dates are found in message
 - Tokens will be given as a range between the given date and now otherwise

If with_fallbacks is set further assumptions will be made including:
 - In the event one date is found it will be assumed the range is since then is now
 - A final fallback will be given as a range covering the current month
 
"""
def get_date_range_from_string(text, with_fallbacks = True):
    dates = search_dates(text, languages=["en"])

    if dates == None:
        # Fallback to date month range
        current_date = datetime.now()
        dates = {
            "start_date": datetime.today().replace(day=1),
            "end_date": current_date.replace(day=calendar.monthrange(current_date.year, current_date.month)[1])
        }
    
    else:
        # Grab first 2 dates and sort them (padding with now just incase only 1 date is given)
        sorted_dates = sorted([date[1] for date in [*dates, ('', datetime.now())][:2]])

        dates = {
            'start_date': sorted_dates[0],
            'end_date': sorted_dates[1]
        }
        
    # Convert dates into iso format (For further processing down the line, especially compatibility with athena)
    dates = {key: date.strftime("%Y-%m-%d") for (key, date) in dates.items()}

    return dates

