import requests
import pandas as pd
from config import conf
import datetime
from datetime import timedelta
from db_access.DbCnx import UserDao
from logger import LoggingConfig
import logging


LoggingConfig.setup_logging()

class UserDataProc():

    URL_HISTORICAL = "https://api.weatherstack.com/historical"
    columns_mandatory = ['observation_time','temperature','weather_code','wind_speed',
                         'wind_degree','wind_dir','pressure','precip','humidity',
                         'cloudcover','feelslike','uv_index','visibility','time','city']

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
                'access_key': conf.WEATHER_API_KEY,
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
     

                    
        


                

        

 
