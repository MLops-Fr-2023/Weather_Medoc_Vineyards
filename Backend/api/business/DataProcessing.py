import gdown
import logging
import requests
import datetime
import pandas as pd
from datetime import timedelta
from logger import LoggingConfig
from db_access.DbCnx import UserDao
from business.KeyReturn import KeyReturn
from config.variables import VarEnvSecurApi, VarEnvWeatherApi, UrlData

LoggingConfig.setup_logging()

# Import des variables
varenv_securapi = VarEnvSecurApi()
varenv_weather_api = VarEnvWeatherApi()
URL_data = UrlData()


class UserDataProc():

    URL_HISTORICAL = URL_data.url_historical
    COLUMNS_MANDATORY = ['observation_time', 'temperature', 'weather_code', 'wind_speed',
                         'wind_degree', 'wind_dir', 'pressure', 'precip', 'humidity',
                         'cloudcover', 'feelslike', 'uv_index', 'visibility', 'time', 'city']
    NB_DAYS = 59
    FILE_ID = varenv_weather_api.file_id
    URL_HIST_DATA = f"https://drive.google.com/uc?id={FILE_ID}"
    WEATHER_DATA_TABLE = 'WEATHER_DATA'

    @staticmethod
    async def insert_weather_data_historical():
        try:
            gdown.download(UserDataProc.URL_HIST_DATA, 'output.csv', quiet=False)
            df = pd.read_csv('output.csv')

            df = df.drop(columns=['Unnamed: 0'])
            df = df.reset_index()
            df.rename(columns={'index': 'id'}, inplace=True)

            # empty table WEATHER_DATA (to avoid duplicates after historical data insertion)
            await UserDao.empty_weather_data()
            # populate table WEATHER_DATA with hostorical data
            await UserDao.send_data_from_df_to_db(df, table_name=UserDataProc.WEATHER_DATA_TABLE)

            logging.info(f"Historical data successfully added to table {UserDataProc.WEATHER_DATA_TABLE}")
            return {KeyReturn.success.value: 'Historical data successfully inserted into db'}
        except Exception as e:
            return {KeyReturn.error.value: f"Historical data insertion failed : {e}"}

    @staticmethod
    def get_data_hist_on_period(city, date_start, date_end):
        """
        Return a dataframe populated with weather data for city on period defined by date_start and date_end
        """
        date_start_str = date_start.strftime("%Y-%m-%d")
        date_end_str = date_end.strftime("%Y-%m-%d")

        params = {
            'access_key': varenv_weather_api.weather_api_key,
            'query': city,
            'historical_date_start': date_start_str,
            'historical_date_end': date_end_str,
            'hourly': '1',
            'interval': '3'
        }

        response = requests.get(UserDataProc.URL_HISTORICAL, params)
        if response.status_code == 200:
            data = response.json()
            df_hist = pd.DataFrame(columns=["observation_time", "temperature", "weather_code", "wind_speed",
                                            "wind_degree", "wind_dir", "pressure", "precip",
                                            "humidity", "cloudcover", "feelslike", "uv_index",
                                            "visibility", "time", "city"])

            for date, date_data in data['historical'].items():
                for hourly_data in date_data['hourly']:
                    temperature = hourly_data['temperature']
                    weather_code = hourly_data['weather_code']
                    wind_speed = hourly_data['wind_speed']
                    wind_degree = hourly_data['wind_degree']
                    wind_dir = hourly_data['wind_dir']
                    pressure = hourly_data['pressure']
                    precip = hourly_data['precip']
                    humidity = hourly_data['humidity']
                    cloudcover = hourly_data['cloudcover']
                    feelslike = hourly_data['feelslike']
                    uv_index = hourly_data['uv_index']
                    visibility = hourly_data['visibility']
                    time = hourly_data['time']
                    city = city

                    row = pd.DataFrame([{
                        "observation_time": date,
                        "temperature": temperature,
                        "weather_code": weather_code,
                        "wind_speed": wind_speed,
                        "wind_degree": wind_degree,
                        "wind_dir": wind_dir,
                        "pressure": pressure,
                        "precip": precip,
                        "humidity": humidity,
                        "cloudcover": cloudcover,
                        "feelslike": feelslike,
                        "uv_index": uv_index,
                        "visibility": visibility,
                        "time": time,
                        "city": city
                    }])
                    df_hist = pd.concat([df_hist, row], ignore_index=True)
                    df_hist['time'] = df_hist['time'].replace({
                        '0': '00:0',
                        '300': '03:00',
                        '600': '06:00',
                        '900': '09:00',
                        '1200': '12:00',
                        '1500': '15:00',
                        '1800': '18:00',
                        '2100': '21:00'})
        else:
            print(f"Failed to get data from WeatherStack API: {response.status_code}")

        return df_hist

    @staticmethod
    async def update_weather_data():
        """
        For all cities in table CITIES, fetch data from Weather API and feed table WEATHER_DATA
         with the available data between last update and today
         For each city : 1 record every 3 hours (8 records/day)
        """

        # data_hist = dict()
        cities = UserDao.get_cities()
        nb_days = UserDataProc.NB_DAYS

        for city in cities:

            # date_last <- last date in WEATHER_DATA
            date_last = UserDao.get_last_date_weather(city)
            if date_last is None:
                msg = "No weather data in database. Populate Weather table before trying to update data"
                return {KeyReturn.error.value: msg}

            # No need to update if last date in WEATHER_DATA is today (data has already been updated)
            if date_last.strftime('%Y-%m-%d') == datetime.date.today().strftime('%Y-%m-%d'):
                return {KeyReturn.success.value: "Data already up to date"}

            # date_start <- the day after the last date in WEATHER_DATA
            date_start = (date_last + timedelta(days=1)).date()
            date_end = datetime.date.today()

            delta_days = (date_end - date_start).days

            # df_hist <- weather data for all cities from date_start to date_end
            df_hist = pd.DataFrame(columns=UserDataProc.COLUMNS_MANDATORY)

            for i in range(0, delta_days, nb_days):  # loop over each 60-day period (because of weatherstack limitation)

                date_start_period = date_start + timedelta(days=i)
                date_end_period = min(date_start_period + timedelta(days=nb_days), date_end)

                # get historical data from weatherstack API
                df_temp = UserDataProc.get_data_hist_on_period(city=city,
                                                               date_start=date_start_period,
                                                               date_end=date_end_period)

                df_hist = pd.concat([df_hist, df_temp], ignore_index=True)

            print(f"\nUpdating table WEATHER_DATA for '{city}'...")
            try:
                success = await UserDao.send_data_from_df_to_db(df_hist, 'WEATHER_DATA')
                if success:
                    msg = f"Weather data for '{city}' successfully updated\n"
                    print(msg)
                    logging.info(msg)

            except Exception as e:
                msg = f"Weather data update for '{city}' failed because of {e}\n"
                print(msg)
                logging.exception(msg)
                return {KeyReturn.error.value: msg}

            msg = "Weather data successfully updated for all cities"
            logging.info(msg)
        return {KeyReturn.success.value: msg}
