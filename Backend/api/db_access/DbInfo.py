from db_access.DbType import DbType

class DbInfo():

    def __init__(self, config):
        self.db_env = config['DB_ENV'] 
        if self.db_env == DbType.snowflake.value:            
            self.db_name = config['DB_SNOWFLAKE']
            self.db_user = config['USER_SNOWFLAKE']
            self.db_pwd  = config['PWD_SNOWFLAKE']
            self.db_account = config['ACCOUNT_SNOWFLAKE']
            self.db_warehouse = config['WAREHOUSE_SNOWFLAKE']
            self.db_schema = config['SCHEMA_SNOWFLAKE']
        elif self.db_env == DbType.mysql.value:
            self.db_host  = config['DB_MYSQL_HOST']
            self.db_name  = config['DB_MYSQL_DBNAME']
            self.db_user  = config['DB_MYSQL_USER']
            self.db_pwd   = config['DB_MYSQL_USR_PWD']