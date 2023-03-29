import logging
from botocore.exceptions import ClientError
from s3_client import init_client


def delete_bucket(bucket_name):
    s3 = init_client()
    try:
        s3.delete_bucket(Bucket=bucket_name)
        logging.info(f"Bucket {bucket_name} deleted successfully.")
    except ClientError as e:
        logging.error(f"Error deleting bucket {bucket_name}: {e}")