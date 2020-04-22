import boto3
import os

from .S3Client import S3Client

def getS3Client():
    config = {
        "service_name": "s3",
        # Serverless local creds 
        "aws_access_key_id": "S3RVER",
        "aws_secret_access_key": "S3RVER"
    }

    env = os.getenv("ENV", 'prod') 
    
    if env == 'prod':
        config["aws_access_key_id"]=os.getenv("AWS_S3_USER_ACCESS_KEY_ID")
        config["aws_secret_access_key"]=os.getenv("AWS_S3_USER_SECRET")
        config["region_name"]=os.getenv("AWS_S3_USER_REGION")

    else:
        # In the event we are in dev mode try to connect to the local instance
        config["endpoint_url"] = "http://localhost:{port}".format(port=os.getenv("LOCAL_S3_PORT",4569)) 
    session = boto3.session.Session()
    client = session.client(
        **config
    )

    return S3Client(
        client,
        os.getenv("AWS_S3_BUCKET_NAME", "")
    )