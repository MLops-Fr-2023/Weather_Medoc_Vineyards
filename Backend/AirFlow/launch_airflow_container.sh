# shutting down previous containers
docker-compose down 

# create folders if not already done
mkdir -p ./dags ./logs ./plugins

echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env

docker-compose up airflow-init

docker-compose up -d
