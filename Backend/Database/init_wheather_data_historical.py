import pandas as pd
import gdown
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL
from dotenv import dotenv_values

def send_data_to_db(df, engine, nb_rec):    
    k = 1
    terminated = False
    nb_loops = df.shape[0] // nb_rec + 1
    while not terminated:
        print(f"Loop {k} on {nb_loops}")
        if k*nb_rec < df.shape[0]:
            df_tmp = df[(k-1)*nb_rec : k*nb_rec]
        else:
            df_tmp = df[(k-1)*nb_rec :]
            terminated = True
        
        df_tmp.to_sql(name='WEATHER_DATA', con=engine, if_exists = 'append', index=False)
        k += 1

config = {**dotenv_values(".env_db")}

db_env = config['DB_ENV']

mysql_host = config['DB_MYSQL_HOST']
mysql_db   = config['DB_MYSQL_DBNAME']
mysql_usr  = config['DB_MYSQL_USER']
mysql_pwd  = config['DB_MYSQL_USR_PWD']

snflk_usr = config['USER_SNOWFLAKE']
snflk_pwd = config['PWD_SNOWFLAKE']
snflk_act = config['ACCOUNT_SNOWFLAKE']
snflk_wh  = config['WAREHOUSE_SNOWFLAKE']
snflk_db  = config['DB_SNOWFLAKE']
snflk_sch = config['SCHEMA_SNOWFLAKE']

file_id = config['FILE_ID']
url = f"https://drive.google.com/uc?id={file_id}"

# Limit number of lines to send at a time to each database system
LIM_REC_SNFLK = 16384
LIM_REC_MYSQL = 150000

gdown.download(url, 'output.csv', quiet=False)
df = pd.read_csv('output.csv')

df = df.drop(columns=['Unnamed: 0'])
df = df.reset_index()
df.rename(columns = {'index':'id'}, inplace = True)

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
    
send_data_to_db(df, engine, nb_rec)