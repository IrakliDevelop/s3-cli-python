import os
import logging
from collections import defaultdict
from botocore.exceptions import ClientError

from s3_utils.s3_client import init_client

def move_files_to_extension_folders(bucket_name):
    s3 = init_client()

    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        objects = response.get("Contents", [])

        moved_files_count = defaultdict(int)

        for obj in objects:
            file_key = obj["Key"]
            file_ext = os.path.splitext(file_key)[1][1:]
            new_key = f"{file_ext}/{file_key}"

            if new_key != file_key:
                s3.copy_object(Bucket=bucket_name, CopySource={"Bucket": bucket_name, "Key": file_key}, Key=new_key)
                s3.delete_object(Bucket=bucket_name, Key=file_key)
                moved_files_count[file_ext] += 1

        return dict(moved_files_count)
    except ClientError as e:
        logging.error(f"Error moving files in bucket {bucket_name}: {e}")
        return None
