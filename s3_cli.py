'''
Run with - python s3_cli.py <command> [arguments]
'''

import argparse
import os
import logging
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

def init_client():
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION")

    return boto3.client("s3", region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)

def list_buckets():
    s3 = init_client()
    response = s3.list_buckets()
    return [bucket["Name"] for bucket in response["Buckets"]]

def create_bucket(bucket_name):
    s3 = init_client()
    try:
        s3.create_bucket(Bucket=bucket_name)
        logging.info(f"Bucket {bucket_name} created successfully.")
    except ClientError as e:
        logging.error(f"Error creating bucket {bucket_name}: {e}")

def delete_bucket(bucket_name):
    s3 = init_client()
    try:
        s3.delete_bucket(Bucket=bucket_name)
        logging.info(f"Bucket {bucket_name} deleted successfully.")
    except ClientError as e:
        logging.error(f"Error deleting bucket {bucket_name}: {e}")

def bucket_exists(bucket_name):
    s3 = init_client()
    try:
        s3.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        return False

def download_file_and_upload_to_s3(url, bucket_name, object_name):
    import requests

    response = requests.get(url)
    if response.status_code == 200:
        s3 = init_client()
        try:
            s3.put_object(Bucket=bucket_name, Key=object_name, Body=response.content)
            logging.info(f"File {object_name} uploaded to bucket {bucket_name} successfully.")
        except ClientError as e:
            logging.error(f"Error uploading file {object_name} to bucket {bucket_name}: {e}")
    else:
        logging.error(f"Error downloading file from URL: {url}")

def set_object_access_policy(bucket_name, object_name, access_level):
    s3 = init_client()
    try:
        s3.put_object_acl(Bucket=bucket_name, Key=object_name, ACL=access_level)
        logging.info(f"Access policy for object {object_name} in bucket {bucket_name} set to {access_level}.")
    except ClientError as e:
        logging.error(f"Error setting access policy for object {object_name} in bucket {bucket_name}: {e}")

def generate_public_read_policy(bucket_name):
    policy = {
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
    return policy

def create_bucket_policy(bucket_name, policy):
    s3 = init_client()
    try:
        s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
        logging.info(f"Bucket policy created for {bucket_name} successfully.")
    except ClientError as e:
        logging.error(f"Error creating bucket policy for {bucket_name}: {e}")

def read_bucket_policy(bucket_name):
    s3 = init_client()
    try:
        response = s3.get_bucket_policy(Bucket=bucket_name)
        return json.loads(response["Policy"])
    except ClientError as e:
        logging.error(f"Error reading bucket policy for {bucket_name}: {e}")
    return None

def main():
    parser = argparse.ArgumentParser(description="A simple CLI for managing AWS S3 buckets.")
    subparsers = parser.add_subparsers(dest="command")
    list_parser = subparsers.add_parser("list", help="List all S3 buckets")
    create_parser = subparsers.add_parser("create", help="Create a new S3 bucket")
    create_parser.add_argument("bucket_name", help="Name of the new bucket")

    delete_parser = subparsers.add_parser("delete", help="Delete an existing S3 bucket")
    delete_parser.add_argument("bucket_name", help="Name of the bucket to delete")

    args = parser.parse_args()

    if args.command == "list":
        buckets = list_buckets()
        print("Buckets:")
        for bucket in buckets:
            print(f"- {bucket}")

    elif args.command == "create":
        create_bucket(args.bucket_name)

    elif args.command == "delete":
        delete_bucket(args.bucket_name)

if name == "main":
    main()
