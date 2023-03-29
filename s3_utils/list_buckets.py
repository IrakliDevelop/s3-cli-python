from s3_client import init_client

def list_buckets():
    s3 = init_client()
    response = s3.list_buckets()
    return [bucket["Name"] for bucket in response["Buckets"]]