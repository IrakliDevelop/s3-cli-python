import logging
from botocore.exceptions import ClientError
from s3_client import init_client

def list_file_versions(bucket_name):
    s3 = init_client()

    try:
        response = s3.list_object_versions(Bucket=bucket_name)
        versions = response.get("Versions", [])

        file_versions = []
        for version in versions:
            file_versions.append(
                {
                    "Key": version["Key"],
                    "VersionId": version["VersionId"],
                    "LastModified": version["LastModified"],
                }
            )

        return file_versions
    except ClientError as e:
        logging.error(f"Error listing file versions for bucket {bucket_name}: {e}")
        return None