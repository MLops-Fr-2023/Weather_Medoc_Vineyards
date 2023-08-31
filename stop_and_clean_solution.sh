#!/bin/bash

# Stop and remove backend containers 
cd Backend
source ./init_path_vars.sh
docker-compose down
cd ..

# Stop and remove frontend containers 
cd Frontend
source ./init_path_vars.sh
docker-compose down
cd ..

# Remove all unused networks
docker network prune -f

# remove running containers and existing volumes
CONTAINERS=$(docker ps -aq)
VOLUMES=$(docker volume ls -q)

if [ -n "$CONTAINERS" ]; then
  docker stop $CONTAINERS
  docker rm $CONTAINERS  
else
  echo "No running containers to stop."
fi

if [ -n "$VOLUMES" ]; then
  docker volume rm $VOLUMES
else
  echo "No volume to remove"
fi
