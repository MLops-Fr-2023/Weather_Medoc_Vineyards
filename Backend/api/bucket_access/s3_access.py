
import logging
import boto3


class s3_access():
    session = boto3.Session()
    s3 = session.resource('s3')
    bucket_name = 'datalake-weather-castle'


class S3LogHandler(logging.StreamHandler):

    def __init__(self, bucket_name, log_path):
        super().__init__()
        self.bucket_name = bucket_name
        self.log_path = log_path
        self.session = boto3.Session()
        self.s3 = self.session.resource('s3')

    def emit(self, record):
        log_message = self.format(record)
        
        # Upload log message to S3 bucket
        self.s3.Object(self.bucket_name, self.log_path).put(Body=log_message)