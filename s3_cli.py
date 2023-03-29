"""
Run with - python s3_cli.py <command> [arguments]

Example: Uploading small and large files to S3 bucket:
$ python s3_cli.py upload-small <file_path> <bucket_name> [--object-name <object_name>]
$ python s3_cli.py upload-large <file_path> <bucket_name> [--object-name <object_name>] [--part-size <part_size>]

Example: add lifecycle policy to delete objects after 120 days:L
$ python s3_cli.py set-lifecycle-policy <bucket_name> [--days <days>]
"""

import argparse
import os
import logging
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Importing s3_utils
from s3_utils.s3_client import init_client
from s3_utils.list_buckets import list_buckets
from s3_utils.create_bucket import create_bucket
from s3_utils.delete_bucket import delete_bucket
from s3_utils.bucket_exists import bucket_exists
from s3_utils.download_file_and_upload_to_s3 import download_file_and_upload_to_s3
from s3_utils.upload_file import upload_small_file, upload_large_file
from s3_utils.bucket_policy import set_object_access_policy,\
    read_bucket_policy,\
    create_bucket_policy,\
    generate_public_read_policy,\
    create_lifecycle_policy
from s3_utils.check_versioning_status import check_versioning_status
from s3_utils.list_file_versions import list_file_versions

load_dotenv()
logging.basicConfig(level=logging.INFO)


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

    check_versioning_parser = subparsers.add_parser("check-versioning", help="Check if versioning is enabled for an S3 bucket")
    check_versioning_parser.add_argument("bucket_name", help="Name of the bucket")

    list_file_versions_parser = subparsers.add_parser("list-file-versions", help="List file versions in an S3 bucket")
    list_file_versions_parser.add_argument("bucket_name", help="Name of the bucket")


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
    elif args.command == "check-versioning":
        versioning_status = check_versioning_status(args.bucket_name)
        print(f"Versioning status for bucket {args.bucket_name}: {versioning_status}")
    elif args.command == "list-file-versions":
        file_versions = list_file_versions(args.bucket_name)
        print("File versions:")
        for version in file_versions:
            print(f"  Key: {version['Key']}, VersionId: {version['VersionId']}, LastModified: {version['LastModified']}")



if __name__ == '__main__':
    main()
