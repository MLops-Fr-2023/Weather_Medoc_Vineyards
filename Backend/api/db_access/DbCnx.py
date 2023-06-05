from snowflake.connector import connect, DictCursor
from dotenv import dotenv_values
from business.User import UserInDB
import json

config = {**dotenv_values(".env_API")}

########### Snowflake IDs #############

USER = config['USER_SNOWFLAKE']
PASSWORD = config['PWD_SNOWFLAKE']
ACCOUNT = config['ACCOUNT_SNOWFLAKE']
WAREHOUSE = config['WAREHOUSE_SNOWFLAKE']
DATABASE = config['DB_SNOWFLAKE']
SCHEMA = config['SCHEMA_SNOWFLAKE']

class DbCnx(): 

    @staticmethod
    def get_db_cnx():
        db_cnx = connect(
            user=USER,
            password=PASSWORD,
            account=ACCOUNT,
            warehouse=WAREHOUSE,
            database=DATABASE,
            schema=SCHEMA
        )
        return db_cnx


class UserDao():

    @staticmethod
    def get_users():
        ctx = DbCnx.get_db_cnx()
        cs = ctx.cursor(DictCursor)
        try:
            request = "SELECT * FROM USERS"
            cs.execute(request)
            list = cs.fetchall()
    
        finally:
            cs.close()
            ctx.close()

        return list

    @staticmethod
    def get_permissions():
        ctx = DbCnx.get_db_cnx()
        cs = ctx.cursor(DictCursor)
        try:
            request =  "SELECT * FROM USER_PERMISSION"
            cs.execute(request)
            list = cs.fetchall()
            list = [user['USER_ID'] for user in list]

        finally:
            cs.close()
            ctx.close()

        return list
    
    @staticmethod
    def get_user_permissions(user_id):
        ctx = DbCnx.get_db_cnx()
        cs = ctx.cursor(DictCursor)
        try:
            request =  f"SELECT * FROM USER_PERMISSION WHERE user_id = '{user_id}'"
            cs.execute(request)
            list = cs.fetchall()
            list = [permission['PERMISSION_ID'] for permission in list]

        finally:
            cs.close()
            ctx.close()
        return list
    
    @staticmethod
    def get_user(user_id: str):
        users = UserDao.get_users()     
        user_ids = [user['USER_ID'] for user in users]
        for user in users:
            if user['USER_ID'] == user_id:
                user_dict = {key.lower(): value for key, value in user.items()}
                user_dict['permissions'] = UserDao.get_user_permissions(user_id)
                return UserInDB(**user_dict)
    
    @staticmethod
    def add_user(user):
        ctx = DbCnx.get_db_cnx()
        cs = ctx.cursor(DictCursor)
        try:
            request =  f"INSERT INTO users (user_id, pwd_hash, firstname, lastname, user_email, position, create_date, last_upd_date, active) "
            request += f"VALUES ('{user.user_id}', '{user.pwd_hash}', '{user.firstname}', '{user.lastname}', '{user.user_email}', '{user.position}', '{user.create_date}', '{user.last_upd_date}', '{user.active}')"

            cs.execute(request)            
        finally:
            cs.close()
            ctx.close()

        return {'Message ' : "User added"}

    @staticmethod
    def add_user_permission(user_id, permission_id):
        ctx = DbCnx.get_db_cnx()
        cs = ctx.cursor(DictCursor)
        try:
            request =  f"INSERT INTO user_permission (user_id, permission_id) "
            request += f"VALUES ('{user_id}', '{permission_id}')"
            cs.execute(request)
            print('User_permissions added')
        finally:
            cs.close()
            ctx.close()

        return {'Message' : f"Permission {permission_id} successfully given to user {user_id}"}

    @staticmethod
    def edit_user(user):
        ctx = DbCnx.get_db_cnx()
        cs = ctx.cursor(DictCursor)

        request =  f"UPDATE USERS SET "
        request += f"pwd_hash = '{user.pwd_hash}', "
        request += f"firstname = '{user.firstname}', "
        request += f"lastname = '{user.lastname}', "
        request += f"user_email = '{user.user_email}', "
        request += f"position = '{user.position}', "
        request += f"last_upd_date = CURRENT_DATE, "
        request += f"active = '{user.active}' "
        request += f"WHERE user_id = '{user.user_id}';"
        
        try:
            cs.execute(request)        
        finally:
            cs.close()
            ctx.close()
        
        return {'Message' : "User and User_permission updated"}

    @staticmethod
    def delete_user(user_id):
        ctx = DbCnx.get_db_cnx()
        cs = ctx.cursor(DictCursor)
        try:
            request = f"DELETE FROM USERS WHERE user_id = '{user_id}'"
            cs.execute(request)
        finally:
            cs.close()
            ctx.close()

        return {'Message' : "User deleted"}

    @staticmethod
    def delete_user_permissions(user):
        ctx = DbCnx.get_db_cnx()
        cs = ctx.cursor(DictCursor)
        try :
            request = f"DELETE FROM USER_PERMISSION WHERE user_id = '{user.user_id}'"
            cs.execute(request)
        finally:
            cs.close()
            ctx.close()
        
        return {'Message' : f"Permissions for user {user.user_id} successfully deleted"}
