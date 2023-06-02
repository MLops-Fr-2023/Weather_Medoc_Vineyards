from snowflake.connector import connect, DictCursor
from dotenv import dotenv_values
import json
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
 

def fetch_permissions(id_user):
    ctx = get_db_connection()
    cs = ctx.cursor(DictCursor)
    try:
        request = f"SELECT up.user_id, up.permission_id, p.description FROM user_permission up JOIN permissions p ON up.permission_id = p.permission_id WHERE user_id = '{id_user}' "
        cs.execute(request)
        list = cs.fetchall()
        list = [permission['PERMISSION_ID'] for permission in list]

    finally:
        cs.close()

    return list


def add_user_db(user_add):
    ctx = get_db_connection()
    cs = ctx.cursor(DictCursor)
    try:
        request =  f"INSERT INTO users (user_id, pwd_hash, create_date, last_upd_date, active) VALUES ('{user_add.user_id}', '{user_add.pwd_hash}', '{user_add.create_date}', '{user_add.last_upd_date}', '{user_add.active}')"
        cs.execute(request)
        for permission in user_add.permissions:
            request= f"INSERT INTO user_permission (user_id, permission_id) VALUES ('{user_add.user_id}', '{permission}')"
            cs.execute(request)
    finally:
        cs.close()

    return {'Message ' : "User added"}



def fetch_user_id():
    ctx = get_db_connection()
    cs = ctx.cursor(DictCursor)
    try:
        request =  "SELECT * FROM USERS"
        cs.execute(request)
        list = cs.fetchall()
        list = [user['USER_ID'] for user in list]
 
    finally:
        cs.close()

    return list

def fetch_user_permission_user_id():
    ctx = get_db_connection()
    cs = ctx.cursor(DictCursor)
    try:
        request =  "SELECT * FROM USER_PERMISSION"
        cs.execute(request)
        list = cs.fetchall()
        list = [user['USER_ID'] for user in list]

    finally:
        cs.close()

    return list

def fetch_user_permission_permission_id(user_id):
    ctx = get_db_connection()
    cs = ctx.cursor(DictCursor)
    try:
        request =  f"SELECT * FROM USER_PERMISSION WHERE user_id = '{user_id}'"
        cs.execute(request)
        list = cs.fetchall()
        list = [permission['PERMISSION_ID'] for permission in list]

    finally:
        cs.close()
    return list


def add_user_permissions_db(user_permissions_add):
    ctx = get_db_connection()
    cs = ctx.cursor(DictCursor)
    try:
        for permission in user_permissions_add.permissions_id:
            request= f"INSERT INTO user_permission (user_id, permission_id) VALUES ('{user_permissions_add.user_id}', '{permission}')"
            cs.execute(request)
        print('User_permissions added')
    finally:
        cs.close()

    return {'Message' :"User_permissions added"}


def modify_user(user, userpermission_previous, userpermission_desired):
    ctx = get_db_connection()
    cs = ctx.cursor(DictCursor)

    permissions_list = user['permissions']
    user_id = user['user_id']
    user.pop('permissions')
    user.pop('user_id')
    keys = user.keys()
    
    request = "UPDATE Users SET "

    for i,j in zip(keys, user) :
        request =request + f" {i} = {j} ,"
    request = request[:-1]
    request = request + "WHERE user_id = '{user.user_id}';"

    try:
        #User object
        cs.execute(request)
        #UserPermission object
    finally:
        cs.close()
    
    #delete all the permission of the user then add the ones desired
    delete_user_permission(userpermission_previous)
    add_user_permissions_db(userpermission_desired)

    return {'Message' : "User and User_permission updated"}


def delete_user(user_id):
    ctx = get_db_connection()
    cs = ctx.cursor(DictCursor)
    try:
        request = f"DELETE FROM USERS WHERE user_id = '{user_id}'"
        cs.execute(request)
    finally:
        cs.close()

    return {'Message' : "User deleted"}


def delete_user_permission(user):
    ctx = get_db_connection()
    cs = ctx.cursor(DictCursor)
    list_permission_id = fetch_user_permission_permission_id(user.user_id)
    summary = dict()
    try :
        for permission in user.permissions_id :
            if permission in list_permission_id :
                request = f"DELETE FROM USER_PERMISSION WHERE user_id = '{user.user_id}' AND permission_id ='{permission}'"
                cs.execute(request)
                summary[permission] = 'Deleted'
            else :
                summary[permission] = 'Non deleted - Not in the User_permission dB for this specific user_id '
    finally:
        cs.close()
    return summary
