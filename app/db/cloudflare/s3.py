import io
import boto3
from app.core.config import settings

s3_client = boto3.client(
    service_name='s3',
    endpoint_url=settings.CLOUDFLARE_S3_URI,
    aws_access_key_id=settings.CLOUDFLARE_ACCESS_KEY_ID,
    aws_secret_access_key=settings.CLOUDFLARE_SECRET_ACCESS_KEY,
    region_name='auto'
)
