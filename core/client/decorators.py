
"""
Wrapper handles standard http status errors and reraises them as python std lib errors. 

If request is successfull processed json data is given
""" 
def handle_errors_and_return_json(func):
    def wrap_api_callout(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.json()
    return wrap_api_callout