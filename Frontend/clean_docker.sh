#!/bin/bash

docker-compose down
docker network prune -f
docker stop $(docker ps -aq) --force
docker rm $(docker ps -aq) --force
docker volume rm $(docker volume ls -q) --force
docker rmi $(docker images -q) --force
docker builder prune --force
rm -rf ./airflow/logs
rm -rf ./airflow/plugins
