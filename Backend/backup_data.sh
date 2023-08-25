#!/bin/bash

# Load environment variables from the file
source .env

# Create a timestamp for the backup file
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
BACKUP_FILE="/home/baloux/Code/WCM/mlflow_backup_$TIMESTAMP.sql"

#echo $MLFLOW_POSTGRES_USER
#echo $MLFLOW_POSTGRES_DB
#echo $BACKUP_FILE
#echo $MLFLOW_POSTGRES_PASSWORD
#echo $MLFLOW_POSTGRES_PORT
#echo $MLFLOW_POSTGRES_HOST

# Run pg_dump to create the backup
#pg_dump -h localhost -U $MLFLOW_POSTGRES_USER -d $MLFLOW_POSTGRES_DB -p $MLFLOW_POSTGRES_PORT -f $BACKUP_FILE -W
echo "pg_dump -h localhost -U $MLFLOW_POSTGRES_USER -d $MLFLOW_POSTGRES_DB -f $BACKUP_FILE -W"
pg_dump -h localhost -U $MLFLOW_POSTGRES_USER -d $MLFLOW_POSTGRES_DB -f $BACKUP_FILE

# Check the exit code of pg_dump
if [ $? -eq 0 ]; then
    echo "MLflow backup created successfully: $BACKUP_FILE"
else
    echo "MLflow backup failed"
    # You can set up alerts or notifications here
fi
