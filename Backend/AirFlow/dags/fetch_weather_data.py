import requests
import json
import os
import datetime
# import pandas as pd
# from joblib import dump
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from airflow.models import Variable

API_KEY  = ''  
BASE_URL = 'http://localhost:8000/fetch'

my_dag = DAG(
    dag_id='fetch_weather_dag',
    tags=['project', 'MLOps', 'datascientest'],
    schedule_interval='@daily',
    default_args={
        'owner': 'airflow',
        'start_date': days_ago(0)
    },
    catchup=False
)

def fetch_weather_data():
    print('fetch_weather_data running')
    return 'fetch_weather_data terminated'

def process_raw_data():
    print('process_raw_data running')
    return 'process_raw_data terminated'


fetch_weather_data = PythonOperator(
    task_id='fetch_weather_data',
    python_callable=fetch_weather_data,
    dag=my_dag,
    doc="""fetch_weather_data description"""
)

process_raw_data = PythonOperator(
    task_id='process_raw_data',
    python_callable=process_raw_data,
    dag=my_dag,
    doc="""process_raw_data description"""
)

fetch_weather_data >> process_raw_data
