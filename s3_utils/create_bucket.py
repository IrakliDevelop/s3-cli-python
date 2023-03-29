import logging
from botocore.exceptions import ClientError
from s3_client import init_client

def create_bucket(bucket_name):
    s3 = init_client()
    try:
        s3.create_bucket(Bucket=bucket_name)
        logging.info(f"Bucket {bucket_name} created successfully.")
    except ClientError as e:
        logging.error(f"Error creating bucket {bucket_name}: {e}")