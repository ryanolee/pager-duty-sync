
"""
Wrapper handles standard http status errors and reraises them as python std lib errors. 

If request is successfull processed json data is given
""" 
def handle_errors_and_return_json(func):
    def wrap_api_callout(obj, *args, **kwargs):
        result = func(obj, *args, **kwargs)
        return result.json()
    return wrap_api_callout