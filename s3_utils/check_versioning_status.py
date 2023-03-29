import logging
from botocore.exceptions import ClientError
from s3_client import init_client

def check_versioning_status(bucket_name):
    s3 = init_client()

    try:
        response = s3.get_bucket_versioning(Bucket=bucket_name)
        versioning_status = response.get("Status", "Not enabled")
        return versioning_status
    except ClientError as e:
        logging.error(f"Error retrieving versioning status for bucket {bucket_name}: {e}")
        return None
