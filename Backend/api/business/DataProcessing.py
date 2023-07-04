import gdown
import logging
import requests
import datetime
import pandas as pd
from datetime import timedelta
from logger import LoggingConfig
from dotenv import dotenv_values
from db_access.DbCnx import UserDao
from config.variables import varenv_securapi, varenv_weather_api, URL_data

LoggingConfig.setup_logging()

#Import des variables
varenv_securapi = varenv_securapi()
varenv_weather_api = varenv_weather_api()
URL_data = URL_data()

class UserDataProc():

    url_historical = URL_data.url_historical
    columns_mandatory = ['observation_time','temperature','weather_code','wind_speed',
                         'wind_degree','wind_dir','pressure','precip','humidity',
                         'cloudcover','feelslike','uv_index','visibility','time','city']
    
    file_id = varenv_weather_api.file_id
    URL_HIST_DATA = f"https://drive.google.com/uc?id={file_id}"

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

    @staticmethod
    async def insert_weather_data_historical():
        try : 
            gdown.download(UserDataProc.URL_HIST_DATA, 'output.csv', quiet=False)
            df = pd.read_csv('output.csv')

            df = df.drop(columns=['Unnamed: 0'])
            df = df.reset_index()
            df.rename(columns = {'index':'id'}, inplace = True)

            UserDao.send_weather_data_from_df_to_db(df) 
            logging.info(f"Historical data successfully added to table WEATHER_DATA")                                                                            
            return {'success' : 'Historical data successfully inserted into db'}
        except Exception as e:
            return {'error': f"Historical data insertion failed : {e}"}

    @staticmethod
    async def update_weather_data():
        """
        For all cities in table CITIES, fetch data from Weather API and feed table WEATHER_DATA with the available data between last update and today
        For each city : 1 record every 3 hours (8 records/day)
        """

        columns = UserDataProc.columns_mandatory
        response_historical = dict()
        cities = UserDao.get_cities()
                
        for city in cities: 
            df_historical = pd.DataFrame(columns=columns)

            # date_start <- the day after the last date in WEATHER_DATA
            date_start = UserDao.get_last_date_weather(city)
            # No need to update if last date in WEATHER_DATA is today (data has already been updated)
            if date_start.strftime('%Y-%m-%d') == datetime.date.today().strftime('%Y-%m-%d'):
                return {'success' : "Data already up to date"} 
            
            date_start = date_start + timedelta(days=1)
            date_start = date_start.strftime('%Y-%m-%d')
            # date_end <- today
            date_end = datetime.date.today()
            date_end = date_end.strftime('%Y-%m-%d')
            
            params = {
                'access_key': varenv_weather_api.weather_api_key,
                'query': city,
                'historical_date_start': date_start,
                'historical_date_end': date_end,
                'hourly': '1',
                'interval': '3'
            }

            response = requests.get(UserDataProc.URL_HISTORICAL, params)
            response_historical = response.json()

            df_temp = pd.DataFrame.from_dict(response_historical).transpose()
            df_temp = df_temp.drop(['request','location','current'], axis = 0)
            df_temp = df_temp.drop(df_temp.columns[0:29], axis = 1)
            df_temp = df_temp.transpose()
            for j in range(df_temp.shape[0]):
                df_int = df_temp.iloc[j]
                date_int = df_int['historical']['date']
                hourly_int = df_int['historical']['hourly']

                for k in range(len(hourly_int)):
                    df_historical_temp = pd.DataFrame(columns=columns)
                    df_calcul = pd.DataFrame(hourly_int[k])
                    df_historical_temp = pd.concat([df_historical_temp, df_calcul], axis = 0)
                    df_historical_temp[columns[0]] = date_int
                    df_historical_temp['city'] = city 
                    df_historical_temp = df_historical_temp[columns]
                    df_historical = pd.concat([df_historical_temp, df_historical], axis = 0)

            # Conversion of Col time from xxxx in hh:mm
            df_historical['time'] = df_historical['time'].apply(lambda x: ':'.join((x[0:2],x[-2:])) if len(x) == 4 else ':'.join((x[0:1],x[-2:])))

            print(f"\nUpdating table WEATHER_DATA for '{city}'...")
            try:
                success = UserDao.send_weather_data_from_df_to_db(df_historical)    
                if success:
                    msg = f"Weather data for '{city}' successfully updated\n"
                    print(msg)
                    logging.info(msg)

            except Exception as e:
                msg = f"Weather data update for '{city}' failed because of {e}\n"
                print(msg)
                logging.exception(msg)
                return False
            
        return True

    @staticmethod
    async def delete_weather_data():

        return {}
     

                    
        


                

        

 
