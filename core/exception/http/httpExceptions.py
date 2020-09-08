class HTTPException(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code

class AuthException(HTTPException):
    def __init__(self, message):
        super.__init__(self, message, 403)

class BadRequestException(HTTPException):
    def __init__(self, message):
        super.__init__(self, message, 400)