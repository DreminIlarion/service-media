
import os
import boto3
from botocore.exceptions import NoCredentialsError

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ru")
S3_BUCKET = os.getenv("S3_BUCKET", "my-image-bucket")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")

try:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
        endpoint_url=S3_ENDPOINT_URL
    )
except NoCredentialsError:
    s3_client = None
    print("S3 credentials not found")