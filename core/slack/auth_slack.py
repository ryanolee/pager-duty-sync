import hashlib
import hmac
import sys

"""
Code adapted from: https://github.com/slackapi/python-slack-events-api/blob/main/slackeventsapi/server.py
"""
def auth_slack(secret, timestamp, signature, body):
    
    req = str.encode('v0:' + str(timestamp) + ':') + body.encode()
    request_hash = 'v0=' + hmac.new(
        str.encode(secret),
        req, hashlib.sha256
    ).hexdigest()
    
    if hasattr(hmac, "compare_digest"):
        # Compare byte strings for Python 2
        if (sys.version_info[0] == 2):
            return hmac.compare_digest(bytes(request_hash), bytes(signature))
        else:
            return hmac.compare_digest(request_hash, signature)
    else:
        if len(request_hash) != len(signature):
            return False
        result = 0
        if isinstance(request_hash, bytes) and isinstance(signature, bytes):
            for x, y in zip(request_hash, signature):
                result |= x ^ y
        else:
            for x, y in zip(request_hash, signature):
                result |= ord(x) ^ ord(y)
        return result == 0