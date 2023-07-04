import logging
from datetime import datetime 
import os
import boto3
from bucket_access.s3_access import S3LogHandler, s3_access

date_string = datetime.now().strftime('%Y%m%d')
 
def setup_logging():
    os.makedirs('logs', exist_ok=True)
    date_string = datetime.now().strftime('%Y%m%d')
    log_path = f"logs/app_{date_string}.log"

    # Configure logging to write logs to a file
    logging.basicConfig(
        filename=log_path,
        filemode='a',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Add a handler to upload log files to S3
    s3_handler = S3LogHandler(s3_access.bucket_name, log_path)
    logging.getLogger().addHandler(s3_handler)



