from enum import Enum

class Permissions(Enum):
    forecast   = "forecast"
    get_data   = "get_data"
    training   = "training"
    user_add   = "user_add"
    usr_edit   = "usr_edit"
    user_mngt  = "user_management"

class SpecialUsersID(Enum):
    administrator = 'admax'


