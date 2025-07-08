from app.db.cloudflare.s3 import s3_client as client
from app.core.config import settings
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

async def put_object(object_name, object_content):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        executor,
        lambda: client.put_object(
            Bucket=settings.CLOUDFLARE_BUCKET_NAME,
            Key=object_name,
            Body=object_content.file
        )
    )
    return object_name

async def delete_object(object_name):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        executor,
        lambda: client.delete_object(
            Bucket=settings.CLOUDFLARE_BUCKET_NAME,
            Key=object_name
        )
    )
    return object_name

async def get_presigned_url(object_name):
    loop = asyncio.get_event_loop()
    url = await loop.run_in_executor(
        executor,
        lambda: client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': settings.CLOUDFLARE_BUCKET_NAME,
                'Key': object_name,
            }
        )
    )
    return url