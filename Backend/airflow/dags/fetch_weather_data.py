import requests
from datetime import timedelta
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from airflow.models import Variable
import os

user_name = os.environ.get('API_USER')
pwd = os.environ.get('API_PWD')
# List of arguments to pass to the function
cities = ["Arsac", "Ludon-Medoc", "Lamarque", "Castelnau-de-Medoc", "Macau", "Soussan", "Margaux"]

my_dag = DAG(
    dag_id='fetch_weather_dag',
    tags=['project', 'MLOps', 'datascientest'],
    schedule_interval=timedelta(hours=3),
    default_args={
        'start_date': days_ago(0)},
    catchup=True)

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


def my_function(city):
    print('forecast data')
    token_type = Variable.get(key='token_type')
    access_token = Variable.get(key='access_token')
    url = 'http://api:8000/forecast_city/'+city
    headers = {
    "accept": "application/json",
    "Authorization": f"{token_type} {access_token}"}
    requests.post(url, headers=headers)

    return f'process_raw_data terminated for {city}'

fetch_weather_data = PythonOperator(
    task_id='fetch_weather_data',
    python_callable=fetch_weather_data,
    dag=my_dag,
    doc="""use api root token to have it
            use api root to  update data""")


# Define the tasks to call the function with different arguments
for city in cities:
    task = PythonOperator(
        task_id=f'Forecast_for_{city}',
        python_callable=my_function,
        op_args=[city],  # Pass the city as a list
        dag=my_dag)
    
    fetch_weather_data >> task