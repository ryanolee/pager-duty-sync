import json
from core.logging import get_logger

# Get standard lambda proxy response (including the no retry slack response)
def get_lambda_proxy_response(data = {}, success = True, headers={}):
    logger = get_logger()
    response = {
        "statusCode": 200 if success else 500,
        "isBase64Encoded": 'false',
        "headers": {
            **{
                "Content-Type": "application/json",
                "X-Slack-No-Retry": "1"
            },
            **headers
        },
        "body": json.dumps({
            **data,
            "success": success
        })
    }
    
    logger.info('Return value:{0}'.format(response))
    return response