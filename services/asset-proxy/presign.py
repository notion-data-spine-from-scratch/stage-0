import os
import sys

import boto3

bucket = os.environ.get("UPLOAD_BUCKET", "uploads")
key = sys.argv[1] if len(sys.argv) > 1 else ""

session = boto3.session.Session(
    aws_access_key_id="test", aws_secret_access_key="test", region_name="us-east-1"
)

s3 = session.client(
    "s3", endpoint_url=os.getenv("S3_ENDPOINT", "http://localstack:4566")
)

url = s3.generate_presigned_url(
    "put_object",
    Params={"Bucket": bucket, "Key": key},
    ExpiresIn=3600,
)

print(url)
