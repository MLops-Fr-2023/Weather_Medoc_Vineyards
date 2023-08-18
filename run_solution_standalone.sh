#!/bin/bash

source ./stop_and_clean_solution.sh

# Remove and create again Airflow logs and plugins folders
rm -rf ./Backend/airflow/logs
rm -rf ./Backend/airflow/plugins
mkdir ./Backend/airflow/logs ./Backend/airflow/plugins

# Create network "outside"
docker network create outside

# Build and start Backend containers
cd Backend
source ./init_path_vars.sh
source ./.env
docker-compose build
docker-compose up -d
cd ..

# Build and start Frontend containers
cd Frontend
source ./init_path_vars.sh
source ./.env
docker-compose build
docker-compose up -d
cd ..
