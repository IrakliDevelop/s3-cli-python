import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def init_client():
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION")

    return boto3.client("s3",
                        region_name=region,
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key)