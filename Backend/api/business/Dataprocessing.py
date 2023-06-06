import requests
import pandas as pd
from business import References
from config import conf
from datetime import datetime

async def fetch_data(columns = References.columns_mandatory, type_request = 'current', API_KEY = conf.WEATHER_API_KEY):
    
    # collect current data and create DataFrame
    df_current = pd.DataFrame(columns = columns)

    
    # collect current data and create DataFrame
    for city in References.cities:
        df_tmp = {}
        params = {
            'access_key': API_KEY,
            'query': city 
        }
        api_result = requests.get(f'http://api.weatherstack.com/{type_request}', params)
        response = api_result.json()
        current = response['current']
        df_tmp['observation_time'] = response['location']['localtime']
        df_tmp['temperature'] = current['temperature']
        df_tmp['weather_code'] = current['weather_code']
        df_tmp['wind_speed'] = current['wind_speed']
        df_tmp['wind_degree'] = current['wind_degree']
        df_tmp['wind_dir'] = current['wind_dir']
        df_tmp['pressure'] = current['pressure']
        df_tmp['precip'] = current['precip']
        df_tmp['humidity'] = current['humidity']
        df_tmp['cloudcover'] = current['cloudcover']
        df_tmp['feelslike'] = current['feelslike']
        df_tmp['uv_index'] = current['uv_index']
        df_tmp['visibility'] = current['visibility']
        df_tmp['time'] = current['observation_time']
        df_tmp['city'] = city
        df_tmp = pd.DataFrame(data=df_tmp,index=[0])
        df_current = pd.concat([df_current, df_tmp])

    df_current.reset_index(inplace=True, drop=True)

    # Modify DataFrame to have same strutucre than historical Dataframe
    for i in range(df_current.shape[0]):
        x, y = df_current['observation_time'][i].split(' ')
        df_current['observation_time'][i] = x
        time = datetime.strptime(df_current['time'][i], "%I:%M %p")
        df_current['time'][i] = time.strftime('%H:%M')

    return df_current