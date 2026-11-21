from app.config import settings
from botocore.config import Config
from botocore.exceptions import ClientError
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
    return s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.r2_bucket,
                'Key': key,
                'ContentType': content_type
                },
            ExpiresIn=300,
            )

def create_presigned_get(key):
    return s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.r2_bucket, 'Key': key},
            ExpiresIn=3600,
            ) 

def object_size(key):
    try:
        head = s3.head_object(Bucket=settings.r2_bucket, Key=key)
    except ClientError as e:
        if e.response['Error']['Code'] in ('404', 'NoSuchKey', 'NotFound'):
            return None
        raise
    return head["ContentLength"]

def delete_object(key):
    head = s3.delete_object(Bucket=settings.r2_bucket, Key=key)
