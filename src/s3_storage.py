from contextlib import asynccontextmanager

from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from fastapi import UploadFile
import uuid
import aiofiles


# s3_client = S3Client(
#     access_key=AWS_ACCESS_KEY_ID,
#     secret_key=AWS_SECRET_ACCESS_KEY,
#     endpoint_url=S3_ENDPOINT_URL,
#     bucket_name=S3_BUCKET_NAME,
#     region_name=S3_REGION_NAME,
# )
# await s3_client.get_file("sharafutdinov.png", "sharafutdinov777.png")
# await s3_client.upload_file("src/kosdem.jpg")


class S3Client:
    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            bucket_name: str,
            region_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
            "region_name": region_name,
        }
        self.endpoint_url = endpoint_url
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client


    async def upload_file(self, file: UploadFile, filename: str = None) -> str:
        file_content = await file.read()
        object_name = filename or f"{uuid.uuid4()}_{file.filename}"

        try:
            async with self.get_client() as client:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    Body=file_content,
                    ContentType=file.content_type
                )
                return object_name  # Вернём имя, чтобы, например, сохранить в БД
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise

    async def delete_file(self, object_name: str):
        try:
            async with self.get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=object_name)
                print(f"File {object_name} deleted from {self.bucket_name}")
        except ClientError as e:
            print(f"Error deleting file: {e}")

    async def get_file(self, object_name: str, destination_path: str):
        try:
            async with self.get_client() as client:
                response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
                data = await response["Body"].read()
                with open(destination_path, "wb") as file:
                    file.write(data)
                print(f"File {object_name} downloaded to {destination_path}")
        except ClientError as e:
            print(f"Error downloading file: {e}")

    async def get_file_url(self, object_name: str) -> str:
        return f"{self.endpoint_url}/{self.bucket_name}/{object_name}"
