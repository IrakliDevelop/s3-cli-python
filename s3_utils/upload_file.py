import os
import logging
from botocore.exceptions import ClientError
from s3_client import init_client

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