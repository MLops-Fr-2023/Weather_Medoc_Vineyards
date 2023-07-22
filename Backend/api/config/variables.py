import os
import boto3
import logging
from dotenv import dotenv_values
from db_access.DbType import DbType

config = {**dotenv_values("../.env")}

def get_var_value(config, varname):
    if not config:
        return os.environ.get(varname)
    else:
        return config[varname]

class S3Access():
    def __init__(self):
        self.session = boto3.Session()
        self.s3 = self.session.resource('s3')

class S3VarAccess():
    def __init__(self, config=config):
        self.bucket_name = get_var_value(config,'BUCKET_NAME')                       

class S3LogHandler(logging.StreamHandler):
    def __init__(self, bucket_name, log_path):
        super().__init__()
        self.bucket_name = bucket_name
        self.log_path = log_path
        self.session = boto3.Session(
            aws_access_key_id=get_var_value(config, 'AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=get_var_value(config, 'AWS_SECRET_ACCESS_KEY'),
            region_name=get_var_value(config, 'AWS_DEFAULT_REGION')
        )
        self.s3 = self.session.resource('s3')

    def emit(self, record):
        log_message = self.format(record)
        # Upload log message to S3 bucket
        self.s3.Object(self.bucket_name, self.log_path).put(Body=log_message)

class VarEnvSecurApi():
    def __init__(self, config=config):
        self.secret_key = get_var_value(config, 'SECRET_KEY')
        self.algorithm = get_var_value(config, 'ALGORITHM')
        self.access_token_expire_minutes = get_var_value(config, 'ACCESS_TOKEN_EXPIRE_MINUTES')
    
class VarEnvWeatherApi(): 
    def __init__(self, config=config):
        self.weather_api_key = get_var_value(config, 'WEATHER_API_KEY')
        self.file_id = get_var_value(config, 'FILE_ID')
    
class VarEnvInferenceModel():
    def __init__(self, config=config):
        self.model_inference = get_var_value(config, 'MODEL_INFERENCE')
        self.s3_root = get_var_value(config, 'S3_ROOT_INFERENCE')
        self.path_artifact = get_var_value(config, 'PATH_ARTIFACT_INFERENCE')
        self.fcst_history = get_var_value(config, 'FCST_HISTORY')
        self.fcst_horizon = get_var_value(config, 'FCST_HORIZON')

class VarEnvMLflow():
    def __init__(self, config=config):
        self.mlflow_server_port = get_var_value(config, 'MLFLOW_SERVER_PORT')

class DbInfo():
    def __init__(self, config=config):
        self.db_env = get_var_value(config, 'DB_ENV')
        if self.db_env == DbType.snowflake.value:            
            self.db_name = get_var_value(config, 'DB_SNOWFLAKE')
            self.db_user = get_var_value(config, 'USER_SNOWFLAKE')
            self.db_pwd  = get_var_value(config, 'PWD_SNOWFLAKE')
            self.db_account = get_var_value(config, 'ACCOUNT_SNOWFLAKE')
            self.db_warehouse = get_var_value(config, 'WAREHOUSE_SNOWFLAKE')
            self.db_schema = get_var_value(config, 'SCHEMA_SNOWFLAKE')
        elif self.db_env == DbType.mysql.value:
            self.db_host  = get_var_value(config, 'DB_MYSQL_HOST')
            self.db_name  = get_var_value(config, 'MYSQL_DATABASE')
            self.db_user  = get_var_value(config, 'DB_MYSQL_USER')
            self.db_pwd   = get_var_value(config, 'MYSQL_ROOT_PASSWORD')

class UrlData():
    def __init__(self, config=config):
        self.url_historical = get_var_value(config, 'URL_HISTORICAL')