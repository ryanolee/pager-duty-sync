import json
from core.logging import get_logger

def get_response(eventName, data = {}):
    logger = get_logger()
    response = {
       "EVENT_TYPE": eventName,
       "PAYLOAD": data
    }
    
    logger.info('Return value:{0}'.format(response))
    return response
    