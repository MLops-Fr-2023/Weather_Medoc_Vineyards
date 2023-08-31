#!/bin/bash
source ./init_path_vars.sh
docker-compose down

#Clean leger (on garde le cache)
docker network prune -f

