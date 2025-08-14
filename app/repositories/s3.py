from app.db.cloudflare.s3 import s3_client as client
from app.core.config import settings
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.utils.logging import logger

executor = ThreadPoolExecutor()

logger = logger.bind(layer="repository", module="s3")

async def put_object(object_key, object_content):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        executor,
        lambda: client.put_object(
            Bucket=settings.CLOUDFLARE_BUCKET_NAME,
            Key=object_key,
            Body=object_content.file
        )
    )
    return object_key

async def delete_object(object_key):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        executor,
        lambda: client.delete_object(
            Bucket=settings.CLOUDFLARE_BUCKET_NAME,
            Key=object_key
        )
    )
    return object_key

async def get_presigned_url(object_key):
    loop = asyncio.get_event_loop()
    url = await loop.run_in_executor(
        executor,
        lambda: client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': settings.CLOUDFLARE_BUCKET_NAME,
                'Key': object_key,
            }
        )
    )
    return url
