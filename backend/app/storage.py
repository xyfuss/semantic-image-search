from app.config import settings
from botocore.config import Config
import boto3

s3 = boto3.client(
       's3',
       endpoint_url=settings.r2_endpoint_url,
       aws_access_key_id=settings.r2_access_key,
       aws_secret_access_key=settings.r2_secret_access_key,
       region_name="auto",
       config=Config(signature_version='s3v4')
)

def create_presigned_put(key, content_type):
    # TODO: write content

def create_presigned_get(key):
    # TODO: write content

def object_size(key):
    # TODO: write content

def delete_object(key):
    # TODO: write content
