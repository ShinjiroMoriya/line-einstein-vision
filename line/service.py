import json


def json_loads(data):
    try:
        return json.loads(data)
    except:
        return data


def json_dumps(data, indent=4):
    try:
        return json.dumps(data, indent=indent)
    except:
        return data
