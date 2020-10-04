from dateparser.search import search_dates
from datetime import datetime

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

"""
def get_date_range_from_string(text):
    dates = search_dates(text, languages=["en"])
    
    print("DATES:", dates, "FROM:", text)

    if dates == None:
        return None

    # Grab first 2 dates and sort them (padding with now just incase only 1 date is given)
    sorted_dates = sorted([date[1] for date in [*dates, ('', datetime.now())][:2]])

    return {
        'start_date': sorted_dates[0],
        'end_date': sorted_dates[1]
    }
