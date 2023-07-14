#!/bin/bash
docker-compose down

#Clean leger (on garde le cache)
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker volume rm $(docker volume ls -q)
rm -rf ./airflow/logs
rm -rf ./airflow/plugins


mkdir ./airflow/logs ./airflow/plugins
sudo echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env.uid

#sudo docker-compose build --no-cache
docker-compose build
docker-compose up
