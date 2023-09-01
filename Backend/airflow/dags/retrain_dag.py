from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
import requests
import os

user_name = os.environ.get('API_USER')
pwd = os.environ.get('API_PWD')
n_epochs = os.environ.get('N_EPOCHS')
API_BASE_URL = os.environ.get('API_BASE_URL')


def get_token():
    """
    Fetch the api to have the access token
    """
    print('get token')
    url_token = f'{API_BASE_URL}/token'
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
    Variable.set(key='token_type', value=token_type)
    Variable.set(key='access_token', value=access_token)


def evaluation(task_instance):
    """
    Connect to the api to evaluate the model
    """
    print('evaluation in progress')
    token_type = Variable.get(key='token_type')
    access_token = Variable.get(key='access_token')
    url = f"{API_BASE_URL}" + "/evaluate_model/{city}?name_city=Margaux"
    headers = {
        "accept": "application/json",
        "Authorization": f"{token_type} {access_token}"}
    answer = requests.post(url, headers=headers)

    if answer.status_code == 200:
        print(answer.json())
        Temperature_mse = answer.json()['TEMPERATURE_MSE']
        Precip_mse = answer.json()['PRECIP_MSE']
        task_instance.xcom_push(key='temperature_mse',
                                value=Temperature_mse)
        task_instance.xcom_push(key='precip_mse',
                                value=Precip_mse)
        return 'model evaluate'
    else:
        raise Exception("Retrain model failed with status code : ", answer.status_code)


def retrain(task_instance):

    Temperature_mse = task_instance.xcom_pull(key='temperature_mse',
                                              task_ids='evaluation')
    Precip_mse = task_instance.xcom_pull(key='precip_mse',
                                         task_ids='evaluation')

    if Temperature_mse > 6 or Precip_mse > 0.1:
        print('retrain in progress')
        token_type = Variable.get(key='token_type')
        access_token = Variable.get(key='access_token')
        url = f"{API_BASE_URL}" + "/retrain_model/{city}?n_epochs=" + str(n_epochs) + "&name_city=Margaux"
        headers = {
            "accept": "application/json",
            "Authorization": f"{token_type} {access_token}"}
        answer = requests.post(url, headers=headers)

        if answer.status_code == 200:
            return 'model retained'
        else:
            raise Exception("Retrain model failed with status code : ", answer.status_code)

    else:
        return f"""not necessary to retrain the model, temperature mse : {Temperature_mse},
        precipitation mse : {Precip_mse}"""


my_dag = DAG(
    dag_id='retrain_model',
    tags=['project', 'MLOps', 'datascientest'],
    schedule_interval='@daily',
    default_args={
        'start_date': days_ago(0)},
    catchup=False)

get_token = PythonOperator(
    task_id='get_token',
    python_callable=get_token,
    dag=my_dag,
    doc="""get token to access the api""")

evaluation = PythonOperator(
    task_id='evaluation',
    python_callable=evaluation,
    dag=my_dag,
    doc="""Evaluate the model with new data""")

retrain_model = PythonOperator(
    task_id='retrain_model',
    python_callable=retrain,
    dag=my_dag,
    doc="""If necessary retrain the model with new data""")

get_token >> evaluation >> retrain_model
