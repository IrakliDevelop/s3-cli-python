import json
import logging
from botocore.exceptions import ClientError
from s3_client import init_client

def set_object_access_policy(bucket_name, object_name, access_level):
    s3 = init_client()
    try:
        s3.put_object_acl(Bucket=bucket_name, Key=object_name, ACL=access_level)
        logging.info(f"Access policy for object {object_name} in bucket {bucket_name} set to {access_level}.")
    except ClientError as e:
        logging.error(f"Error setting access policy for object {object_name} in bucket {bucket_name}: {e}")

def read_bucket_policy(bucket_name):
    s3 = init_client()
    try:
        response = s3.get_bucket_policy(Bucket=bucket_name)
        return json.loads(response["Policy"])
    except ClientError as e:
        logging.error(f"Error reading bucket policy for {bucket_name}: {e}")
    return None

def create_bucket_policy(bucket_name, policy):
    s3 = init_client()
    try:
        s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
        logging.info(f"Bucket policy created for {bucket_name} successfully.")
    except ClientError as e:
        logging.error(f"Error creating bucket policy for {bucket_name}: {e}")

def generate_public_read_policy(bucket_name):
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]
    }

def create_lifecycle_policy(bucket_name, days=120):
    s3 = init_client()

    lifecycle_configuration = {
        "Rules": [
            {
                "ID": "Delete objects after 120 days",
                "Status": "Enabled",
                "Filter": {},
                "Expiration": {"Days": days},
            }
        ]
    }

    try:
        s3.put_bucket_lifecycle_configuration(Bucket=bucket_name, LifecycleConfiguration=lifecycle_configuration)
        logging.info(f"Lifecycle policy created for bucket {bucket_name} to delete objects after {days} days.")
    except ClientError as e:
        logging.error(f"Error creating lifecycle policy for bucket {bucket_name}: {e}")