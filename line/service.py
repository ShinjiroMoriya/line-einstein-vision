import json
import jwt
import time
from datetime import datetime, timedelta
from django.conf import settings as st


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


def jwt_encode(data):
    exp_time = datetime.now() + timedelta(days=1)
    exp_time = int(time.mktime(exp_time.timetuple()))

    data.update({
        'exp': exp_time,
    })

    encode = jwt.encode(data, st.SECRET_KEY)
    return encode.decode("utf-8")


def jwt_decode(data):
    try:
        return jwt.decode(data, st.SECRET_KEY)
    except Exception as ex:
        print(ex)
        return None
