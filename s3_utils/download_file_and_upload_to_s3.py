import logging
from botocore.exceptions import ClientError
from s3_client import init_client


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