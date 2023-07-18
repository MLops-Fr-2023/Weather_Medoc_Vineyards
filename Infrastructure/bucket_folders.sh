#!/bin/bash

##################################
######### Bucket Folders #########
##################################

# Replace <bucket-name> with your actual bucket name
# Replace <folder-name> with the name of the folder you want to create

# For the 'logs' folder
aws s3api put-object --bucket wine-castle-storage --key logs/

# For the 'streamlit' folder
aws s3api put-object --bucket wine-castle-storage --key streamlit/

# For the 'mlflow' folder
aws s3api put-object --bucket wine-castle-storage --key mlflow/

# For the 'team' folder inside 'streamlit'
aws s3api put-object --bucket wine-castle-storage --key streamlit/team/

# For the 'images' folder inside 'streamlit'
aws s3api put-object --bucket wine-castle-storage --key streamlit/images/

#Copy the documents from the repo to the bucket
aws s3 cp ~/Wheather_MEDOC_VINEYARDS/bucket_documents/team/ s3://<bucket_name>/team/
aws s3 cp ~/Wheather_MEDOC_VINEYARDS/bucket_documents/images/ s3://<bucket_name>/images/