from snowflake.connector import connect, DictCursor
from dotenv import dotenv_values
config = {**dotenv_values(".env_API")}

########### Snowflake IDs #############

USER_SNOWFLAKE = config['USER_SNOWFLAKE']
PWD_SNOWFLAKE = config['PWD_SNOWFLAKE']
ACCOUNT_SNOWFLAKE = config['ACCOUNT_SNOWFLAKE']
WAREHOUSE_SNOWFLAKE = config['WAREHOUSE_SNOWFLAKE']
DB_SNOWFLAKE = config['DB_SNOWFLAKE']
SCHEMA_SNOWFLAKE = config['SCHEMA_SNOWFLAKE']


######## Snowflake Functions ##########


def get_db_connection():
    db_cnx = connect(
        user=USER_SNOWFLAKE,
        password=PWD_SNOWFLAKE,
        account=ACCOUNT_SNOWFLAKE,
        warehouse=WAREHOUSE_SNOWFLAKE,
        database=DB_SNOWFLAKE,
        schema=SCHEMA_SNOWFLAKE
    )
    return db_cnx

def fetch_users_from_db():
    ctx = get_db_connection()
    cs = ctx.cursor(DictCursor)
    try:
        cs.execute("SELECT * FROM users WHERE active = TRUE")
        users = cs.fetchall()
    finally:
        cs.close()

    return {user['USER_ID']: user for user in users}
 
# test_1 = fetch_users_from_db
# print(test_1)

def fetch_permissions(id_user):
    ctx = get_db_connection()
    cs = ctx.cursor(DictCursor)
    try:
        request = f"SELECT up.user_id, up.permission_id, p.description FROM user_permission up JOIN permissions p ON up.permission_id = p.permission_id WHERE user_id = '{id_user}' "
        cs.execute(request)
        list = cs.fetchall()
        # dict_permission = {permission['PERMISSION_ID'] : permission['DESCRIPTION'] for permission in list} Si besoin d'un dictionnaire
        list_permission = [permission['PERMISSION_ID'] for permission in list]
    finally:
        cs.close()

    return list_permission


def add_user_db(user_add):
    ctx = get_db_connection()
    cs = ctx.cursor(DictCursor)
    try:
        request_user_add =  f"INSERT INTO users (user_id, pwd_hash, create_date, last_upd_date, active) VALUES ('{user_add.user_id}', '{user_add.pwd_hash}', '{user_add.create_date}', '{user_add.last_upd_date}', '{user_add.active}')"
        cs.execute(request_user_add)
        print('User added')
        for permission in user_add.permission:
            request_user_permission_add = f"INSERT INTO user_permission (user_id, permission_id) VALUES ('{user_add.user_id}', '{permission}')"
            cs.execute(request_user_permission_add)
        print('User_permissions added')
    finally:
        cs.close()

    return "User and User_permissions added"
