import os
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)


def upload_file_to_s3(local_file_path: str, s3_key: str):
    try:
        s3.upload_file(
            local_file_path,
            AWS_BUCKET_NAME,
            s3_key
        )

        return {
            "status": "success",
            "message": f"Uploaded {local_file_path} to s3://{AWS_BUCKET_NAME}/{s3_key}"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }