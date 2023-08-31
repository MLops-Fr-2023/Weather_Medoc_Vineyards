#!/bin/bash
source ./init_path_vars.sh
#docker-compose down

#Clean leger (on garde le cache)
#docker network prune -f
#docker stop $(docker ps -aq)
#docker rm $(docker ps -aq)
#docker volume rm $(docker volume ls -q)
#rm -rf ./airflow/logs
#rm -rf ./airflow/plugins

#mkdir ./airflow/logs ./airflow/plugins
source ./.env

# Create the "outside" network
docker network create outside
docker-compose build api mlflow_server mlflow_postgresql nginx_proxy
docker-compose up api mlflow_server mlflow_postgresql nginx_proxy
