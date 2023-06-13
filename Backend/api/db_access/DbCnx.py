from snowflake.connector import connect, DictCursor
from dotenv import dotenv_values
from business.User import UserInDB, UserAdd, User
from business.UserPermission import UserPermission
from mysql.connector import connect as connect_mysql
from mysql.connector.cursor_cext import CMySQLCursorDict
from snowflake.connector import connect as connect_sf, DictCursor 
from enum import Enum
from db_access.DbInfo import DbInfo
from db_access.DbType import DbType
from config import conf
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL

config = {**dotenv_values(".env_API")}

db_info = DbInfo(config)

class DbCnx(): 

    @staticmethod
    def get_db_cnx():
        db_cnx = None
        if db_info.db_env == DbType.snowflake.value:
            db_cnx = connect_sf(
                user      = db_info.db_user,
                password  = db_info.db_pwd,
                account   = db_info.db_account,
                warehouse = db_info.db_warehouse,
                database  = db_info.db_name,
                schema    = db_info.db_schema
            )
        elif db_info.db_env == DbType.mysql.value:
            db_cnx = connect_mysql(
                user      = db_info.db_user,
                password  = db_info.db_pwd,
                host      = db_info.db_host,
                database  = db_info.db_name)
    
        return db_cnx


class UserDao():

    @staticmethod
    def get_cursor(db_env: str, ctx):
        """
        Return the appropriate Dictionnary Cursor depending on database environment 
        """
        if db_env == DbType.snowflake.value:
            cs = ctx.cursor(DictCursor)
        elif db_env == DbType.mysql.value:
            cs = ctx.cursor(cursor_class=CMySQLCursorDict)
        return cs

    @staticmethod
    def get_users():
        """
        Get all users from table USERS
        """
        ctx = DbCnx.get_db_cnx()
        cs = UserDao.get_cursor(db_info.db_env, ctx)
        try:
            request = "SELECT * FROM USERS"
            cs.execute(request)
            users = cs.fetchall()
        finally:
            cs.close()
            ctx.close()

        return users

    @staticmethod
    def user_exists(user_id: str):
        """
        Return a boolean indicating whether the user exists in table USERS
        """
        user = UserDao.get_user(user_id)
        return user is not None
    
    @staticmethod
    def get_permission_ids():
        """
        Get all permissions from table PERMISSIONS
        """
        ctx = DbCnx.get_db_cnx()
        cs = UserDao.get_cursor(db_info.db_env, ctx)
        try:
            request = "SELECT * FROM PERMISSIONS"
            cs.execute(request)
            permissions_dic = cs.fetchall()
            permission_ids = [permission_dic['PERMISSION_ID'] for permission_dic in permissions_dic]
        finally:
            cs.close()
            ctx.close()

        return permission_ids



    @staticmethod
    def get_user_permissions(user_id: str):
        """
        Get all permissions for user_id from table USER_PERMISSION
        """
        ctx = DbCnx.get_db_cnx()
        cs = UserDao.get_cursor(db_info.db_env, ctx)
        try:
            request =  f"SELECT * FROM USER_PERMISSION WHERE USER_ID = '{user_id}'"
            cs.execute(request)
            permissions = cs.fetchall()
            permission_ids = [permission['PERMISSION_ID'] for permission in permissions]

        finally:
            cs.close()
            ctx.close()
        return permission_ids
    
    @staticmethod
    def user_has_permission(userPermission: UserPermission):
        """
        Return a boolean indicating whether the user_id has the permission permission_id in table USER_PERMISSION
        """
        ctx = DbCnx.get_db_cnx()
        cs = ctx.cursor(DictCursor)
        try:
            request =  f"SELECT USER_ID, PERMISSION_ID FROM USER_PERMISSION "
            request += f"WHERE user_id = '{userPermission.user_id}' AND permission_id = '{userPermission.permission_id}'"
            cs.execute(request)
            cnt = cs.fetchall()
            value = len(cnt) > 0
        finally:
            cs.close()
            ctx.close()
        return value
    
    @staticmethod
    def get_user(user_id: str):
        """
        Get user with id user_id from table USERS
        """
        users = UserDao.get_users()   
        user_ids = [user['USER_ID'] for user in users]
        for user in users:
            if user['USER_ID'] == user_id:                
                user_dict = {key.lower(): value for key, value in user.items()}
                user_dict['permissions'] = UserDao.get_user_permissions(user_id)
                return UserInDB(**user_dict)
        
    @staticmethod
    def add_user(user: UserAdd):
        """
        Add new user in table USERS
        """
        ctx = DbCnx.get_db_cnx()
        cs = UserDao.get_cursor(db_info.db_env, ctx)
        try:
            request =  f"INSERT INTO USERS (USER_ID, PWD_HASH, FIRSTNAME, LASTNAME, USER_EMAIL, POSITION, CREATE_DATE, LAST_UPD_DATE, ACTIVE) "
            request += f"VALUES ('{user.user_id}', '{user.pwd_hash}', '{user.firstname}', '{user.lastname}', '{user.user_email}', '{user.position}', CURRENT_DATE, CURRENT_DATE, '{user.active}')"
            cs.execute(request)            
            ctx.commit()           
        finally:
            cs.close()
            ctx.close()

        return {'Message ' : f"User '{user.user_id}' created"}

    @staticmethod
    def add_user_permission(userPermission: UserPermission):
        """
        Give permission_id to user_id by adding record in table USER_PERMISSION
        """
        ctx = DbCnx.get_db_cnx()
        cs = UserDao.get_cursor(db_info.db_env, ctx)
        try:
            request =  f"INSERT INTO USER_PERMISSION (USER_ID, PERMISSION_ID) "
            request += f"VALUES ('{userPermission.user_id}', '{userPermission.permission_id}')"
            cs.execute(request)
            ctx.commit()
            print(f"Permission '{userPermission.permission_id}' successfully given to user '{userPermission.user_id}'")
        finally:
            cs.close()
            ctx.close()

        return {'Message' : f"Permission '{userPermission.permission_id}' successfully given to user '{userPermission.user_id}'"}

    @staticmethod
    def edit_user(user: User):
        """
        Update user in table USERS with user given in input
        """
        ctx = DbCnx.get_db_cnx()
        cs = UserDao.get_cursor(db_info.db_env, ctx)

        request =  f"UPDATE USERS SET "
        request += f"PWD_HASH = '{user.pwd_hash}', "
        request += f"FIRSTNAME = '{user.firstname}', "
        request += f"LASTNAME = '{user.lastname}', "
        request += f"USER_EMAIL = '{user.user_email}', "
        request += f"POSITION = '{user.position}', "
        request += f"LAST_UPD_DATE = CURRENT_DATE, "
        request += f"ACTIVE = '{user.active}' "
        request += f"WHERE USER_ID = '{user.user_id}';"
        
        try:
            cs.execute(request)    
            ctx.commit()    
        finally:
            cs.close()
            ctx.close()
        
        return {'Message' : f"User {user.user_id} successfully updated"}

    @staticmethod
    def delete_user(user_id: str):
        """
        Delete user_id's permissions from table USER_PERMISSION
        then delete user_id from table USERS
        """
        # delete user's permissions first because of integrity constraints
        UserDao.delete_user_permissions(user_id)
        ctx = DbCnx.get_db_cnx()
        cs = UserDao.get_cursor(db_info.db_env, ctx)        
        try:            
            request = f"DELETE FROM USERS WHERE USER_ID = '{user_id}'"
            cs.execute(request)
            ctx.commit()
        finally:
            cs.close()
            ctx.close()

        return {'Message' : f"User '{user_id}' and related permissions successfully deleted"}

    @staticmethod
    def delete_user_permission(userPermission: UserPermission):
        """
        Delete record (user_id, permission_id) from table USER_PERMISSION
        """
        ctx = DbCnx.get_db_cnx()
        cs = UserDao.get_cursor(db_info.db_env, ctx)
        try :
            request = f"DELETE FROM USER_PERMISSION WHERE USER_ID = '{userPermission.user_id}' AND PERMISSION_ID = '{userPermission.permission_id}'"
            cs.execute(request)
            ctx.commit()
        finally:
            cs.close()
            ctx.close()
        
        return {'Message' : f"Permission '{userPermission.permission_id}' for user {userPermission.user_id} successfully deleted"}

    @staticmethod
    def delete_user_permissions(user_id: str):
        """
        Delete all permissions associated to user_id in table USER_PERMISSION
        """
        ctx = DbCnx.get_db_cnx()
        cs = UserDao.get_cursor(db_info.db_env, ctx)
        try :
            request = f"DELETE FROM USER_PERMISSION WHERE USER_ID = '{user_id}'"
            cs.execute(request)
            ctx.commit()
        finally:
            cs.close()
            ctx.close()
        
        return {'Message' : f"Permissions for user {user_id} successfully deleted"}

    @staticmethod
    def get_cities():
        """
        Get all cities from table CITIES
        """
        ctx = DbCnx.get_db_cnx()
        cs = UserDao.get_cursor(db_info.db_env, ctx)
        try:
            request = "SELECT CITY FROM CITIES"
            cs.execute(request)
            cities_dic = cs.fetchall()
            cities = [city_dic['CITY'] for city_dic in cities_dic ]
        finally:
            cs.close()
            ctx.close()

        return cities

    @staticmethod
    def get_last_date_weather(city: str):
        ctx = DbCnx.get_db_cnx()
        cs = UserDao.get_cursor(db_info.db_env, ctx)
        request =  f"SELECT max(OBSERVATION_TIME) as LAST_DATE FROM WEATHER_DATA "
        request += f"WHERE CITY = '{city}'"
        try:
            cs.execute(request)    
            last_date_dic = cs.fetchone()
            last_date = last_date_dic['LAST_DATE']
        finally:
            cs.close()
            ctx.close()
        
        return last_date
    
    @staticmethod
    def send_weather_data_from_df_to_db(df):   
        db_env = conf.DB_ENV
        mysql_host, mysql_db, mysql_usr, mysql_pwd = [conf.DB_MYSQL_HOST, conf.DB_MYSQL_DBNAME, conf.DB_MYSQL_USER, conf.DB_MYSQL_USR_PWD]
        snflk_usr, snflk_pwd, snflk_act, snflk_wh, snflk_db, snflk_sch = [conf.USER_SNOWFLAKE, conf.PWD_SNOWFLAKE, conf.ACCOUNT_SNOWFLAKE, 
                                                                        conf.WAREHOUSE_SNOWFLAKE, conf.DB_SNOWFLAKE, conf.SCHEMA_SNOWFLAKE]
        
        # Limit number of lines to send at a time to each database system
        LIM_REC_SNFLK = 16384
        LIM_REC_MYSQL = 150000

        try:
            if db_env == "mysql":
                    engine = create_engine(f"mysql+mysqlconnector://{mysql_usr}:{mysql_pwd}@{mysql_host}/{mysql_db}", echo=False)
                    nb_rec = LIM_REC_MYSQL   
                
            elif db_env == "snowflake":
                engine = create_engine(URL(
                    user      = snflk_usr,
                    password  = snflk_pwd,
                    account   = snflk_act,
                    database  = snflk_db,
                    schema    = snflk_sch,
                    warehouse = snflk_wh,
                ))
                nb_rec = LIM_REC_SNFLK  
        except Exception as e:
            print(f"Engine creation failed for DB {db_env} : {e}")
            return False
        try:
            k = 1
            terminated = False
            nb_loops = df.shape[0] // nb_rec + 1
            while not terminated:
                # print(f"Loop {k} on {nb_loops}")
                if k*nb_rec < df.shape[0]:
                    df_tmp = df[(k-1)*nb_rec : k*nb_rec]
                else:
                    df_tmp = df[(k-1)*nb_rec :]
                    terminated = True
                
                df_tmp.to_sql(name='WEATHER_DATA', con=engine, if_exists = 'append', index=False)
                k += 1
            return True
        except Exception as e:
            print(f"Data insertion into table WEATHER_DATA failed : {e}")
            return False
        
        return True
