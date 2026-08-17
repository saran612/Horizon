from minio import Minio
from app.core.config import settings

# Initialize MinIO client
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE
)

def ensure_bucket_exists(bucket_name: str = settings.MINIO_BUCKET_NAME) -> None:
    """
    Checks if a bucket exists, and creates it if it doesn't.
    """
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"MinIO bucket '{bucket_name}' created successfully.")
        else:
            print(f"MinIO bucket '{bucket_name}' already exists.")
    except Exception as e:
        print(f"Error checking/creating MinIO bucket '{bucket_name}': {e}")
        raise e
