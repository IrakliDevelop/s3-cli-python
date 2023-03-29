'''
Run with - python s3_cli.py <command> [arguments]

Example: Uploading small and large files to S3 bucket:
$ python s3_cli.py upload-small <file_path> <bucket_name> [--object-name <object_name>]
$ python s3_cli.py upload-large <file_path> <bucket_name> [--object-name <object_name>] [--part-size <part_size>]

Example: add lifecycle policy to delete objects after 120 days:L
$ python s3_cli.py set-lifecycle-policy <bucket_name> [--days <days>]
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

def upload_small_file(file_path, bucket_name, object_name=None):
    s3 = init_client()
    object_name = object_name or os.path.basename(file_path)

    with open(file_path, "rb") as file:
        try:
            s3.put_object(Bucket=bucket_name, Key=object_name, Body=file)
            logging.info(f"File {object_name} uploaded to bucket {bucket_name} successfully.")
        except ClientError as e:
            logging.error(f"Error uploading file {object_name} to bucket {bucket_name}: {e}")

def upload_large_file(file_path, bucket_name, object_name=None, part_size=5 * 1024 * 1024):
    s3 = init_client()
    object_name = object_name or os.path.basename(file_path)

    try:
        # Create a multipart upload
        response = s3.create_multipart_upload(Bucket=bucket_name, Key=object_name)
        upload_id = response["UploadId"]

        parts = []
        part_number = 1

        with open(file_path, "rb") as file:
            while True:
                data = file.read(part_size)
                if not data:
                    break

                # Upload the part
                response = s3.upload_part(Bucket=bucket_name, Key=object_name, PartNumber=part_number, UploadId=upload_id, Body=data)
                parts.append({"PartNumber": part_number, "ETag": response["ETag"]})
                part_number += 1

        # Complete the multipart upload
        s3.complete_multipart_upload(Bucket=bucket_name, Key=object_name, UploadId=upload_id, MultipartUpload={"Parts": parts})
        logging.info(f"Large file {object_name} uploaded to bucket {bucket_name} successfully.")
    except ClientError as e:
        logging.error(f"Error uploading large file {object_name} to bucket {bucket_name}: {e}")
        s3.abort_multipart_upload(Bucket=bucket_name, Key=object_name, UploadId=upload_id)

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


def main():
    parser = argparse.ArgumentParser(description="A simple CLI for managing AWS S3 buckets.")
    subparsers = parser.add_subparsers(dest="command")
    upload_small_parser = subparsers.add_parser("upload-small", help="Upload a small file to an S3 bucket")
    upload_small_parser.add_argument("file_path", help="Path to the file to be uploaded")
    upload_small_parser.add_argument("bucket_name", help="Name of the target bucket")
    upload_small_parser.add_argument("--object-name", help="Name of the object in the S3 bucket (default: same as file name)")

    upload_large_parser = subparsers.add_parser("upload-large", help="Upload a large file to an S3 bucket")
    upload_large_parser.add_argument("file_path", help="Path to the file to be uploaded")
    upload_large_parser.add_argument("bucket_name", help="Name of the target bucket")
    upload_large_parser.add_argument("--object-name", help="Name of the object in the S3 bucket (default: same as file name)")
    upload_large_parser.add_argument("--part-size", type=int, default=5 * 1024 * 1024, help="Size of each part in bytes (default: 5MB)")

    list_parser = subparsers.add_parser("list", help="List all S3 buckets")
    create_parser = subparsers.add_parser("create", help="Create a new S3 bucket")
    create_parser.add_argument("bucket_name", help="Name of the new bucket")

    delete_parser = subparsers.add_parser("delete", help="Delete an existing S3 bucket")
    delete_parser.add_argument("bucket_name", help="Name of the bucket to delete")

    set_lifecycle_policy_parser = subparsers.add_parser("set-lifecycle-policy", help="Create a lifecycle policy to delete objects after a specified number of days")
    set_lifecycle_policy_parser.add_argument("bucket_name", help="Name of the target bucket")
    set_lifecycle_policy_parser.add_argument("--days", type=int, default=120, help="Number of days after which objects should be deleted (default: 120)")


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
    elif args.command == "upload-small":
        upload_small_file(args.file_path, args.bucket_name, object_name=args.object_name)

    elif args.command == "upload-large":
        upload_large_file(args.file_path, args.bucket_name, object_name=args.object_name, part_size=args.part_size)
    elif args.command == "set-lifecycle-policy":
        create_lifecycle_policy(args.bucket_name, days=args.days)



if __name__ == '__main__':
    main()
