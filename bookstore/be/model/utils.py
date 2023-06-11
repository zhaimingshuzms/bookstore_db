import time
import json

ORDER_EXPIRED_TIME_INTERVAL = 10


def check_expired(timestamp: float) -> bool:
    """Check whether an order is expired."""
    # print(time.time() - timestamp)
    if time.time() - timestamp > ORDER_EXPIRED_TIME_INTERVAL:
        return True
    return False

def to_dict(model):
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}

def serialize_dict(data_dict):
    for key in data_dict:
        if not isinstance(data_dict[key], str) and not isinstance(data_dict[key], int):
            data_dict[key] = json.dumps(data_dict[key])
    return data_dict