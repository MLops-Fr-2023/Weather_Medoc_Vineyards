#!/bin/bash

docker-compose down

docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

docker rmi $(docker images -aq)
docker volume rm $(docker volume ls -q)
docker builder prune --force


sudo docker-compose build --no-cache
sudo docker-compose up

