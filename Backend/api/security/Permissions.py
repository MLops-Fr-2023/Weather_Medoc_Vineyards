from enum import Enum

class Permissions(Enum):
    forecast   = "forecast"
    get_data   = "get_data"
    training   = "training"
    user_add   = "user_add"
    usr_edit   = "usr_edit"
    user_mngt  = "user_management"

def is_in_enum(permission):
    return permission in Permissions.__members__