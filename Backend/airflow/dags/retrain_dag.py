from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import requests
import os

user_name = os.environ.get('API_USER')
pwd = os.environ.get('API_PWD')
n_epochs = os.environ.get('N_EPOCHS')


def retrain():
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

    print('retrain in progress')
    url = "http://api:8000/retrain_model/{city}?n_epochs=" + str(n_epochs) + "&name_city=Margaux"
    headers = {
        "accept": "application/json",
        "Authorization": f"{token_type} {access_token}"}
    answer = requests.post(url, headers=headers)
    return 'model retrained'


my_dag = DAG(
    dag_id='retrain_model',
    tags=['project', 'MLOps', 'datascientest'],
    schedule_interval='@daily',
    default_args={
        'start_date': days_ago(0)},
    catchup=False)

retrain_model = PythonOperator(
    task_id='retrain_model',
    python_callable=retrain,
    dag=my_dag,
    doc="""Retrain the model with new data""")

retrain_model
