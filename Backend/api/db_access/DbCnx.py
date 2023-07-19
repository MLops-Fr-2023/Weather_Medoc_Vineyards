import os
import boto3
import logging
import pandas as pd
from enum import Enum
from datetime import datetime
from logger import LoggingConfig
from db_access.DbType import DbType
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
from business.KeyReturn import KeyReturn
from fastapi.responses import HTMLResponse
from business.User import UserInDB, UserAdd, User
from business.UserPermission import UserPermission
from snowflake.connector import connect, DictCursor
from mysql.connector import connect as connect_mysql
from mysql.connector.cursor_cext import CMySQLCursorDict
from snowflake.connector import connect as connect_sf, DictCursor 
from config.variables import S3LogHandler, S3VarAccess, S3Access, DbInfo

# Opening a Boto session to get acces to the bucket S3 of the projet
# The EC2 machine has to be configured with AWS CLI and access Key

# Get info to connect to database and AWS bucket
db_info = DbInfo()
s3_access = S3Access()
s3_var_access = S3VarAccess()

# Logger Import 
LoggingConfig.setup_logging()


class DbCnx(): 

    #Redondance avec Dbinfo
    @staticmethod
    def get_db_cnx(db_cnx_info: DbInfo):
        db_cnx = None
        if db_cnx_info.db_env == DbType.snowflake.value:
            db_cnx = connect_sf(
                user      = db_cnx_info.db_user,
                password  = db_cnx_info.db_pwd,
                account   = db_cnx_info.db_account,
                warehouse = db_cnx_info.db_warehouse,
                database  = db_cnx_info.db_name,
                schema    = db_cnx_info.db_schema
            )
        elif db_info.db_env == DbType.mysql.value:            
            db_cnx = connect_mysql(
                user      = db_cnx_info.db_user,
                password  = db_cnx_info.db_pwd,
                host      = db_cnx_info.db_host,
                database  = db_cnx_info.db_name)
    
        return db_cnx
    
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

class UserDao():

    @staticmethod
    def get_users():
        """
        Get all users from table USERS
        """
        ctx = DbCnx.get_db_cnx(db_info)
        cs = DbCnx.get_cursor(db_info.db_env, ctx)
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
        ctx = DbCnx.get_db_cnx(db_info)
        cs = DbCnx.get_cursor(db_info.db_env, ctx)
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
        ctx = DbCnx.get_db_cnx(db_info)
        cs = DbCnx.get_cursor(db_info.db_env, ctx)
        try:
            request =  f"""
                SELECT * FROM USER_PERMISSION 
                WHERE USER_ID = %s
                """
            cs.execute(request, (user_id,))
            permissions = cs.fetchall()
            permission_ids = [permission['PERMISSION_ID'] for permission in permissions]
        except Exception as e:
            msg = f"Failed to get permissions for user '{user_id}'"
            logging.exception(f"{msg} \n {e}")
            return None
        finally:
            cs.close()
            ctx.close()
        
        return permission_ids
    
    @staticmethod
    def user_has_permission(userPermission: UserPermission):
        """
        Return a boolean indicating whether the user_id has the permission permission_id in table USER_PERMISSION
        """
        ctx = DbCnx.get_db_cnx(db_info)
        cs = ctx.cursor(DictCursor)
        try:
            request =  f"""
                SELECT USER_ID, PERMISSION_ID FROM USER_PERMISSION 
                WHERE USER_ID = %s AND PERMISSION_ID = %s
                """
            cs.execute(request, (userPermission.user_id, userPermission.permission_id))
            cnt = cs.fetchall()
            has_permission = len(cnt) > 0
        except Exception as e:
            logging.exception(f"Failed to check existence of permission '{userPermission.permission_id}' for user '{userPermission.user_id}'")
            return None
        finally:
            cs.close()
            ctx.close()
        return has_permission
    
    @staticmethod
    def get_user(user_id: str):
        """
        Get user with user_id from table USERS
        """
        ctx = DbCnx.get_db_cnx(db_info)
        cs = DbCnx.get_cursor(db_info.db_env, ctx)
        try:
            request = f"""SELECT * FROM USERS WHERE USER_ID = %s"""
            cs.execute(request, (user_id,))
            user_dict = cs.fetchone()
            user_dict = {key.lower(): value for key, value in user_dict.items()}
        except Exception as e:            
            logging.exception(f"Failed to get user with user_id '{user_id}' \n {e}")
            return None
        finally:
            cs.close()
            ctx.close()

        user = User(**user_dict)
        user.permissions = UserDao.get_user_permissions(user.user_id)
        return user
        
    @staticmethod
    def add_user(user: UserAdd):
        """
        Add new user in table USERS
        """
        ctx = DbCnx.get_db_cnx(db_info)
        cs = DbCnx.get_cursor(db_info.db_env, ctx)
        try:
            request = f"""
            INSERT INTO USERS (USER_ID, PWD_HASH, FIRSTNAME, LASTNAME, USER_EMAIL, POSITION, CREATE_DATE, LAST_UPD_DATE, ACTIVE) 
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE, CURRENT_DATE, %s)
            """
            cs.execute(request, (user.user_id, user.pwd_hash, user.firstname, user.lastname, user.user_email, user.position, user.active))  
            ctx.commit()              
        except Exception as e:
            msg = f"User '{user.user_id}' creation failed"
            logging.exception(f"{msg} \n {e}")
            return {KeyReturn.error.value : f"{msg} : {e}"}
        finally:
            cs.close()
            ctx.close()

        msg = f"User '{user.user_id}' created successfully"
        logging.info(msg)
        return {KeyReturn.success.value : msg}

    @staticmethod
    def add_user_permission(userPermission: UserPermission):
        """
        Give permission_id to user_id by adding record in table USER_PERMISSION
        """
        ctx = DbCnx.get_db_cnx(db_info)
        cs = DbCnx.get_cursor(db_info.db_env, ctx)
        try:
            request = f"""
            INSERT INTO USER_PERMISSION (USER_ID, PERMISSION_ID)
            VALUES (%s, %s)
            """            
            cs.execute(request, (userPermission.user_id, userPermission.permission_id))
            ctx.commit()
        except Exception as e:
            msg = f"Failed to give permission '{userPermission.permission_id}' to user '{userPermission.user_id}'"
            logging.exception(f"{msg} \n {e}")
            return {KeyReturn.error.value: f"msg"}
        finally:
            cs.close()
            ctx.close()

        msg = f"Permission '{userPermission.permission_id}' successfully given to user '{userPermission.user_id}'"
        logging.info(msg)
        return {KeyReturn.success.value: msg}

    @staticmethod
    def edit_user(user: User):
        """
        Update user in table USERS with user given in input
        """
        ctx = DbCnx.get_db_cnx(db_info)
        cs = DbCnx.get_cursor(db_info.db_env, ctx)

        request = f"""
            UPDATE USERS SET 
            PWD_HASH = %s,
            FIRSTNAME = %s,
            LASTNAME = %s,
            USER_EMAIL = %s,
            POSITION = %s,
            LAST_UPD_DATE = CURRENT_DATE,
            ACTIVE = %s 
            WHERE USER_ID = %s
            """
        try:
            cs.execute(request, (user.pwd_hash, user.firstname, user.lastname, user.user_email, user.position, user.active, user.user_id))
            ctx.commit()               
        except Exception as e:
            msg = f"Failed to edit user '{user.user_id}'"
            logging.exception(f"{msg} \n {e}")
            return {KeyReturn.error.value: msg}
        finally:
            cs.close()
            ctx.close()
        
        msg = f"User '{user.user_id}' successfully updated"
        logging.info(f"{msg}")
        return {KeyReturn.success.value: msg}

    @staticmethod
    def delete_user(user_id: str):
        """
        Delete user_id's permissions from table USER_PERMISSION
        then delete user_id from table USERS
        """
        # delete user's permissions first because of integrity constraints
        UserDao.delete_user_permissions(user_id)
        ctx = DbCnx.get_db_cnx(db_info)
        cs = DbCnx.get_cursor(db_info.db_env, ctx)        
        try:            
            request = f"""DELETE FROM USERS WHERE USER_ID = %s"""
            cs.execute(request, (user_id,))
            ctx.commit()
        except Exception as e:
            msg = f"Failed to delete user '{user_id}'"
            logging.exception(f"{msg} \n {e}")
            return {KeyReturn.error.value: msg}
        finally:
            cs.close()
            ctx.close()

        msg = f"User '{user_id}' successfully deleted"
        logging.info(msg)
        return {KeyReturn.success.value: msg}        

    @staticmethod
    def delete_user_permission(userPermission: UserPermission):
        """
        Delete record (user_id, permission_id) from table USER_PERMISSION
        """
        ctx = DbCnx.get_db_cnx(db_info)
        cs = DbCnx.get_cursor(db_info.db_env, ctx)
        try :
            request = f"""DELETE FROM USER_PERMISSION WHERE USER_ID = %s AND PERMISSION_ID = %s"""            
            cs.execute(request, (userPermission.user_id, userPermission.permission_id))
            ctx.commit()
        except Exception as e:
            msg = f"Failed to remove permision '{userPermission.permission_id}' to user '{userPermission.user_id}'"
            logging.exception(f"{msg} \n {e}")
            return {KeyReturn.error.value: msg}
        finally:
            cs.close()
            ctx.close()
        
        msg = f"Permission '{userPermission.permission_id}' successfully removed for user '{userPermission.user_id}'"
        logging.info(msg)
        return {KeyReturn.success.value: msg}        

    @staticmethod
    def delete_user_permissions(user_id: str):
        """
        Delete all permissions associated to user_id in table USER_PERMISSION
        """
        ctx = DbCnx.get_db_cnx(db_info)
        cs = DbCnx.get_cursor(db_info.db_env, ctx)
        try :
            request = f"DELETE FROM USER_PERMISSION WHERE USER_ID = '{user_id}'"
            cs.execute(request)
            ctx.commit()
        except Exception as e:
            msg = f"Failed to delete permissions to user '{user_id}'"
            logging.exception(f"{msg} \n {e}")
            return {KeyReturn.error.value: msg}
        finally:
            cs.close()
            ctx.close()
        
        return {KeyReturn.success.value : f"Permissions for user {user_id} successfully deleted"}

    @staticmethod
    def get_cities():
        """
        Get all cities from table CITIES
        """
        ctx = DbCnx.get_db_cnx(db_info)
        cs = DbCnx.get_cursor(db_info.db_env, ctx)
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
        ctx = DbCnx.get_db_cnx(db_info)
        cs = DbCnx.get_cursor(db_info.db_env, ctx)
        request =  f"""SELECT max(OBSERVATION_TIME) as LAST_DATE 
                       FROM WEATHER_DATA 
                       WHERE CITY = %s
                    """        
        try:
            cs.execute(request, (city,))    
            last_date_dic = cs.fetchone()
            last_date = last_date_dic['LAST_DATE']
        finally:
            cs.close()
            ctx.close()
        
        return last_date
    
    @staticmethod
    def empty_weather_data():
        ctx = DbCnx.get_db_cnx(db_info)
        cs = DbCnx.get_cursor(db_info.db_env, ctx)
        request = f"DELETE FROM WEATHER_DATA"        
        try:
            cs.execute(request)                
            ctx.commit()
            logging.info("Delete all records from table WEATHER_DATA")
            return {KeyReturn.success.value: "Weather data successfully deleted"}
        except Exception as e:
            logging.error(f"Data deletion from table WEATHER_DATA failed : {e}")
            return {KeyReturn.error.value: f"Weather data deletion failed : {e}"}
        finally:
            cs.close()
            ctx.close()
    
    @staticmethod
    def get_last_datetime_weather(city: str):
        ctx = DbCnx.get_db_cnx(db_info)
        cs = DbCnx.get_cursor(db_info.db_env, ctx)

        request = """
        SELECT 
            MAX(CASE 
                WHEN LENGTH(TIME) = 5 THEN CONCAT(SUBSTRING(OBSERVATION_TIME, 1, 11), TIME)
                WHEN LENGTH(TIME) = 4 THEN CONCAT(SUBSTRING(OBSERVATION_TIME, 1, 11), '0', TIME)
                ELSE NULL
            END) as LAST_DATETIME
        FROM 
            WEATHER_DATA
        WHERE CITY = %s
        """
        try:            
            ctx.commit()   
            cs.execute(request, (city,))    
            last_datetime_dic = cs.fetchone()
            last_datetime = last_datetime_dic['LAST_DATETIME']
        finally:
            cs.close()
            ctx.close()
        
        return last_datetime

    @staticmethod
    def get_weather_data():
        """
        Get weather data from table WHEATHER_DATA
        """
        ctx = DbCnx.get_db_cnx(db_info)
        cs = DbCnx.get_cursor(db_info.db_env, ctx)
        try:
            request = "SELECT * FROM WEATHER_DATA"
            cs.execute(request)
            weather_data = cs.fetchall()            
        finally:
            cs.close()
            ctx.close()

        return weather_data

    @staticmethod
    def get_weather_data_df():
        weather_dict = UserDao.get_weather_data()
        df = pd.DataFrame(weather_dict)
        df = df.set_index('ID')
        return df

    @staticmethod
    def send_weather_data_from_df_to_db(df):   
        db_env = db_info.db_env
        if db_env == "mysql":
            mysql_host, mysql_db, mysql_usr, mysql_pwd = [db_info.db_host, db_info.db_name, db_info.db_user, db_info.db_pwd]
        elif db_env =="snowflake":
            snflk_usr, snflk_pwd, snflk_act, snflk_wh, snflk_db, snflk_sch = [db_info.db_user, db_info.db_pwd, db_info.db_account,db_info.db_warehouse, db_info.db_name, db_info.db_schema]
        else:
            raise Exception("Invalid database environment")
        
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
            msg = f"Engine creation failed for DB {db_env} : {e}"
            print(msg)
            logging.exception(msg)
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
            msg = f"Data insertion into table WEATHER_DATA failed : {e}"
            print(msg)
            logging.exception(msg)
            return False
        
        return True

    @staticmethod
    def get_logs():
        try:
            #Find the logs
            log_path = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"

            # Download log file from S3 bucket
            s3_access.s3.Object(s3_var_access.bucket_name, log_path).download_file('/tmp/app.log')
            
            # Read the downloaded log file
            with open('/tmp/app.log', 'r') as log_file:
                logs = log_file.read()
            
            # Format logs as HTML response
            formatted_logs = "<pre>" + logs + "</pre>"
            
            return HTMLResponse(content=formatted_logs)
        
        except Exception as e:
            return f"Error retrieving logs for today: {str(e)}"