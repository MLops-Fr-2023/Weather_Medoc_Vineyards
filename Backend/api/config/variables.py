import os
import boto3
import logging
from dotenv import dotenv_values
from db_access.DbType import DbType

config = {**dotenv_values("api.env")}

class S3Access():
    def __init__(self):
        self.session = boto3.Session()
        self.s3 = self.session.resource('s3')

class S3VarAccess():
    def __init__(self, config=config):
        self.bucket_name = config['BUCKET_NAME']
        self.s3_uri = config['S3_URI']
        self.s3_prefix = config['S3_PREFIX']

class S3LogHandler(logging.StreamHandler):
    def __init__(self, bucket_name, log_path):
        super().__init__()
        self.bucket_name = bucket_name
        self.log_path = log_path
        self.session = boto3.Session()
        self.s3 = self.session.resource('s3')

    def emit(self, record):
        log_message = self.format(record)
        # Upload log message to S3 bucket
        self.s3.Object(self.bucket_name, self.log_path).put(Body=log_message)

class VarEnvSecurApi():
    def __init__(self, config=config):
        self.secret_key = os.environ.get('SECRET_KEY')
        self.algorithm = os.environ.get('ALGORITHM')
        self.access_token_expire_minutes = config['ACCESS_TOKEN_EXPIRE_MINUTES']

class VarEnvWeatherApi(): 
    def __init__(self, config=config):
        self.weather_api_key = os.environ.get('WEATHER_API_KEY')
        self.file_id = os.environ.get('FILE_ID')


class VarEnvInferenceModel():
    def __init__(self, config=config):
        self.model_inference = config['MODEL_INFERENCE']
        self.fcst_history = config['FCST_HISTORY']
        self.fcst_horizon = config['FCST_HORIZON']

class VarEnvMLflow():
    def __init__(self, config=config):
        self.mlflow_server_port = config['MLFLOW_SERVER_PORT']
        self.mlflow_exp_name = config['MLFLOW_EXP_NAME']
        self.mlflow_s3_endpoint_url = config['MLFLOW_S3_ENDPOINT_URL']

class DbInfo():
    def __init__(self, config=config):
        self.db_env = config['DB_ENV'] 
        if self.db_env == DbType.snowflake.value:            
            self.db_name = config['DB_SNOWFLAKE']
            self.db_user = os.environ.get('USER_SNOWFLAKE')
            self.db_pwd  = os.environ.get('PWD_SNOWFLAKE')
            self.db_account = os.environ.get('ACCOUNT_SNOWFLAKE')
            self.db_warehouse = config['WAREHOUSE_SNOWFLAKE']
            self.db_schema = config['SCHEMA_SNOWFLAKE']
        elif self.db_env == DbType.mysql.value:
            self.db_host  = config['DB_MYSQL_HOST']
            self.db_name  = config['DB_MYSQL_DBNAME']
            self.db_user  = os.environ.get('DB_MYSQL_USER')
            self.db_pwd   = os.environ.get('DB_MYSQL_USR_PWD')

class UrlData():
    def __init__(self, config=config):
        self.url_historical = config['URL_HISTORICAL']