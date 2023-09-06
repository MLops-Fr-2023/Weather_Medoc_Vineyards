#!/bin/bash
source ./init_path_vars.sh
docker-compose down

#Clean leger (on garde le cache)
docker network prune -f
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker volume rm $(docker volume ls -q)
rm -rf ./airflow/logs
rm -rf ./airflow/plugins

sudo useradd ubuntu
sudo groupadd mlops
sudo usermod -aG mlops ubuntu

mkdir ./airflow/logs ./airflow/plugins

sudo chown -R ubuntu:mlops ./airflow/logs
sudo chmod -R 770 ./airflow/logs

sudo chown -R ubuntu:mlops ./airflow/plugins
sudo chmod -R 770 ./airflow/plugins

source ./.env
source ./init_path_vars.sh

# Create the "outside" network
docker network create outside
docker-compose build
docker-compose up
