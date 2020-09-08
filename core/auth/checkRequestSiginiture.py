import os
import hashlib
import time
import json
import base64
from core.exception.http import AuthException, BadRequestException
from core.logging import get_logger


# Expect payloads to look like
# {
#   "signature": "sha_256",
#   "timestamp": "unix timestamp",
#   "nonce": "some_random_value"
#   "payload": {}
# }
def check_request(wrapped_payload):
    missing_keys = list(set(["signature", "timestamp", "nonce", "payload"]) - set(wrapped_payload.keys()))
    if missing_keys != []:
        raise BadRequestException("Expected payload to have keys " + str(missing_keys))
        
    logger = get_logger()

    secret = os.getenv("API_AUTH_SECRET")
    payload_grace_period = os.getenv("API_AUTH_GRACE_PERIOD", 30)

    timestamp = wrapped_payload["timestamp"]

    # Get if request was generated in the grace period or it is in the future
    if time.time() - timestamp > payload_grace_period or time.time() > timestamp:
        raise AuthException("Request timestamp out of date or in the future")

    #Compute payload
    payload_to_check = "{payload}.{nonce}.{timestamp}.{secret}".format(
           payload = base64.urlsafe_b64decode(json.loads(wrapped_payload["payload"])),
           nonce = wrapped_payload["nonce"],
           timestamp = timestamp,
           secret = secret
    ).decode()
    
    #calc hash
    sha256 = hashlib.sha256()
    sha256.update(payload_to_check)
    if sha256.hexdigest() != wrapped_payload["signature"]:
        raise AuthException("signature mismatch")

def request_validator(func):
    def wrapped_func(*inner_args, **inner_kw_args):
        # In the event the lambda has a body check it
        if len(inner_args) !== 0 and "body" in inner_args[0]:
            wrapped_payload = json.loads(inner_args[0].body)
            check_request(wrapped_payload)
        return func(*inner_args, **inner_kw_args)
    return wrapped_func
