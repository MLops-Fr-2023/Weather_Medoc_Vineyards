import requests
from datetime import timedelta
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from airflow.models import Variable
import os

user_name = os.environ.get('API_USER')
pwd = os.environ.get('API_PWD')

my_dag = DAG(
    dag_id='fetch_weather_dag',
    tags=['project', 'MLOps', 'datascientest'],
    schedule_interval=timedelta(hours=3),
    default_args={
        'start_date': days_ago(0)},
    catchup=False)

def fetch_weather_data():
    print('get token')
    url_token = 'http://api:8000/token'
    headers = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"}
    data = {
    "grant_type": "",
    "username": user_name,
    "password": pwd,
    "scope": "",
    "client_id": "",
    "client_secret": ""}
    answer = requests.post(url_token, headers=headers, data=data)
    token_type = answer.json()['token_type']
    access_token = answer.json()['access_token']
    Variable.set(key = 'token_type', value = token_type)
    Variable.set(key = 'access_token', value = access_token)

    print('fetch_weather_data running')
    url = 'http://api:8000/update_weather_data'
    headers = {
    "accept": "application/json",
    "Authorization": f"{token_type} {access_token}"}
    requests.post(url, headers=headers)

    return 'fetch_weather_data terminated'

def forecast_data():
    print('forecast data')
    token_type = Variable.get(key='token_type')
    access_token = Variable.get(key='access_token')
    url = 'http://api:8000/forecast_city/{city}?name_city=Margaux'
    headers = {
    "accept": "application/json",
    "Authorization": f"{token_type} {access_token}"}
    requests.post(url, headers=headers)

    return 'process_raw_data terminated'

fetch_weather_data = PythonOperator(
    task_id='fetch_weather_data',
    python_callable=fetch_weather_data,
    dag=my_dag,
    doc="""use api root token to have it
            use api root to  update data""")

forecast_data = PythonOperator(
    task_id='forecast_data',
    python_callable=forecast_data,
    dag=my_dag,
    doc="""use api root to forecast data""")

fetch_weather_data >> forecast_data