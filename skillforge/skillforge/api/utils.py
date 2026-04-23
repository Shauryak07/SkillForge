
def success_response(data):
    return {
        "data": data,
        "error" : None
    }

def error_response(code, message):
    return {
        "data" : None,
        "error":{
            "code" : code,
            "message" : message
        }
    }