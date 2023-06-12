The folder *Backend/databases* contains the files to initiate the database behind the API
These files are intended to be used only once at project 1st deployment

##### db_creation_mysql.sql 
This sql script creates the database structure (tables and a few data) for a MySql server
##### db_creation_snowflake.sql 
sql script that creates the database structure (tables and a few data) for a Snowflake warehouse
##### requirements.txt 
list of the python librairies necessary to run init_weather_data_historical.py
##### init_weather_data_historical.py 
Python script that feeds the table WHEATHER_DATA with historical data from the file *historical_20080801.csv*
You may need to upgrade python libraries before running this script with the following command line 
`$ pip install -r requirements.txt`
Use the following command line to launch the script :
`$ python init_weather_data_historical.py`
