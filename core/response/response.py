import json
from core.logging import get_logger

def get_response(success = True, data = {}):
    logger = get_logger()
    response = {
        "statusCode": 200 if success else 500,
        "isBase64Encoded": 'false',
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            **data,
            "success": success
        })
    }
    
    logger.info('Return value:{0}'.format(response))
    return response
    