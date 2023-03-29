from botocore.exceptions import ClientError
from s3_client import init_client


def bucket_exists(bucket_name):
    s3 = init_client()
    try:
        s3.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        return False