import io
from datetime import timedelta
from typing import Optional

from minio import Minio
from minio.error import S3Error

from backend.config import settings


def _validate_bucket(bucket_name: str) -> str:
    if not bucket_name:
        raise ValueError("MinIO bucket name must be provided")
    return bucket_name


def get_minio_client() -> Minio:
    if not settings.minio_endpoint:
        raise ValueError("MinIO endpoint is not configured")
    if not settings.minio_access_key or not settings.minio_secret_key:
        raise ValueError("MinIO access key/secret key is not configured")

    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
    )


def ensure_bucket(bucket_name: str, client: Optional[Minio] = None) -> None:
    client = client or get_minio_client()
    bucket = _validate_bucket(bucket_name)
    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
    except S3Error as exc:
        raise RuntimeError(
            f"Failed to ensure bucket '{bucket}': {exc}") from exc


def upload_file(
    file_path: str,
    object_name: str,
    bucket_name: str,
    content_type: Optional[str] = None,
    client: Optional[Minio] = None,
) -> str:
    client = client or get_minio_client()
    bucket = _validate_bucket(bucket_name)
    ensure_bucket(bucket, client)

    try:
        client.fput_object(bucket, object_name, file_path,
                           content_type=content_type)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to upload file '{file_path}': {exc}") from exc

    return object_name


def upload_bytes(
    data: bytes,
    object_name: str,
    bucket_name: str,
    content_type: Optional[str] = None,
    client: Optional[Minio] = None,
) -> str:
    client = client or get_minio_client()
    bucket = _validate_bucket(bucket_name)
    ensure_bucket(bucket, client)

    stream = io.BytesIO(data)
    length = len(data)
    try:
        client.put_object(
            bucket,
            object_name,
            stream,
            length,
            content_type=content_type,
        )
    except S3Error as exc:
        raise RuntimeError(
            f"Failed to upload bytes to '{object_name}': {exc}") from exc

    return object_name


def download_file(
    object_name: str,
    file_path: str,
    bucket_name: str,
    client: Optional[Minio] = None,
) -> None:
    client = client or get_minio_client()
    bucket = _validate_bucket(bucket_name)

    try:
        client.fget_object(bucket, object_name, file_path)
    except S3Error as exc:
        raise RuntimeError(
            f"Failed to download '{object_name}': {exc}") from exc


def download_bytes(
    object_name: str,
    bucket_name: str,
    client: Optional[Minio] = None,
) -> bytes:
    client = client or get_minio_client()
    bucket = _validate_bucket(bucket_name)

    try:
        response = client.get_object(bucket, object_name)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()
    except S3Error as exc:
        raise RuntimeError(
            f"Failed to download '{object_name}': {exc}") from exc


def get_presigned_get_url(
    object_name: str,
    bucket_name: str,
    expires: timedelta = timedelta(hours=1),
    client: Optional[Minio] = None,
) -> str:
    client = client or get_minio_client()
    bucket = _validate_bucket(bucket_name)

    try:
        return client.presigned_get_object(bucket, object_name, expires=expires)
    except S3Error as exc:
        raise RuntimeError(f"Failed to create presigned URL: {exc}") from exc


def remove_object(
    object_name: str,
    bucket_name: str,
    client: Optional[Minio] = None,
) -> None:
    client = client or get_minio_client()
    bucket = _validate_bucket(bucket_name)

    try:
        client.remove_object(bucket, object_name)
    except S3Error as exc:
        raise RuntimeError(f"Failed to remove '{object_name}': {exc}") from exc
