import io
from datetime import timedelta

import pytest
from minio import Minio
from minio.error import S3Error

from backend.console.dal.tos import client as tos_client


class TestMinioValidation:
    """Test validation functions."""

    def test_validate_bucket_with_valid_name(self):
        result = tos_client._validate_bucket("test-bucket")
        assert result == "test-bucket"

    def test_validate_bucket_with_empty_name(self):
        with pytest.raises(ValueError, match="MinIO bucket name must be provided"):
            tos_client._validate_bucket("")

    def test_validate_bucket_with_none(self):
        with pytest.raises(ValueError, match="MinIO bucket name must be provided"):
            tos_client._validate_bucket(None)


class TestMinioClient:
    """Test MinIO client operations."""

    def test_get_minio_client_success(self, minio_settings):
        client = tos_client.get_minio_client()
        assert isinstance(client, Minio)
        assert client._base_url.host == minio_settings["endpoint"]

    def test_get_minio_client_missing_endpoint(self, monkeypatch):
        from backend.config import settings
        monkeypatch.setattr(settings, "minio_endpoint", None)
        with pytest.raises(ValueError, match="MinIO endpoint is not configured"):
            tos_client.get_minio_client()

    def test_get_minio_client_missing_credentials(self, monkeypatch):
        from backend.config import settings
        monkeypatch.setattr(settings, "minio_access_key", None)
        with pytest.raises(ValueError, match="MinIO access key/secret key is not configured"):
            tos_client.get_minio_client()


class TestBucketOperations:
    """Test bucket operations."""

    def test_ensure_bucket_creates_new_bucket(self, minio_client, test_bucket):
        # Bucket should already exist from fixture
        assert minio_client.bucket_exists(test_bucket)

    def test_ensure_bucket_with_existing_bucket(self, minio_client, test_bucket):
        # Call again - should not raise error
        tos_client.ensure_bucket(test_bucket, minio_client)
        assert minio_client.bucket_exists(test_bucket)

    def test_ensure_bucket_with_invalid_name(self, minio_client):
        with pytest.raises(ValueError, match="MinIO bucket name must be provided"):
            tos_client.ensure_bucket("", minio_client)


class TestFileUpload:
    """Test file upload operations."""

    def test_upload_bytes_success(self, minio_client, test_bucket):
        data = b"test data content"
        object_name = "test-upload.txt"

        result = tos_client.upload_bytes(
            data=data,
            object_name=object_name,
            bucket_name=test_bucket,
            content_type="text/plain",
            client=minio_client,
        )

        assert result == object_name
        # Verify upload
        obj = minio_client.get_object(test_bucket, object_name)
        assert obj.read() == data
        obj.close()
        obj.release_conn()

    def test_upload_bytes_with_empty_data(self, minio_client, test_bucket):
        data = b""
        object_name = "empty-file.txt"

        result = tos_client.upload_bytes(
            data=data,
            object_name=object_name,
            bucket_name=test_bucket,
            client=minio_client,
        )

        assert result == object_name

    def test_upload_file_success(self, minio_client, test_bucket, tmp_path):
        # Create a temporary file
        test_file = tmp_path / "test.txt"
        test_content = "test file content"
        test_file.write_text(test_content)

        object_name = "uploaded-test.txt"
        result = tos_client.upload_file(
            file_path=str(test_file),
            object_name=object_name,
            bucket_name=test_bucket,
            content_type="text/plain",
            client=minio_client,
        )

        assert result == object_name
        # Verify upload
        obj = minio_client.get_object(test_bucket, object_name)
        assert obj.read().decode() == test_content
        obj.close()
        obj.release_conn()

    def test_upload_file_with_invalid_path(self, minio_client, test_bucket):
        with pytest.raises(RuntimeError, match="Failed to upload file"):
            tos_client.upload_file(
                file_path="/non/existent/file.txt",
                object_name="test.txt",
                bucket_name=test_bucket,
                client=minio_client,
            )


class TestFileDownload:
    """Test file download operations."""

    def test_download_bytes_success(self, minio_client, test_bucket):
        # Upload test data first
        test_data = b"test download data"
        object_name = "test-download.txt"
        minio_client.put_object(
            test_bucket,
            object_name,
            io.BytesIO(test_data),
            len(test_data),
        )

        # Download
        result = tos_client.download_bytes(
            object_name=object_name,
            bucket_name=test_bucket,
            client=minio_client,
        )

        assert result == test_data

    def test_download_bytes_nonexistent_object(self, minio_client, test_bucket):
        with pytest.raises(RuntimeError, match="Failed to download"):
            tos_client.download_bytes(
                object_name="nonexistent.txt",
                bucket_name=test_bucket,
                client=minio_client,
            )

    def test_download_file_success(self, minio_client, test_bucket, tmp_path):
        # Upload test data first
        test_data = b"test file download"
        object_name = "test-file-download.txt"
        minio_client.put_object(
            test_bucket,
            object_name,
            io.BytesIO(test_data),
            len(test_data),
        )

        # Download to file
        download_path = tmp_path / "downloaded.txt"
        tos_client.download_file(
            object_name=object_name,
            file_path=str(download_path),
            bucket_name=test_bucket,
            client=minio_client,
        )

        assert download_path.read_bytes() == test_data

    def test_download_file_nonexistent_object(self, minio_client, test_bucket, tmp_path):
        download_path = tmp_path / "downloaded.txt"
        with pytest.raises(RuntimeError, match="Failed to download"):
            tos_client.download_file(
                object_name="nonexistent.txt",
                file_path=str(download_path),
                bucket_name=test_bucket,
                client=minio_client,
            )


class TestPresignedUrl:
    """Test presigned URL generation."""

    def test_get_presigned_get_url_success(self, minio_client, test_bucket):
        # Upload test data first
        test_data = b"test presigned url data"
        object_name = "test-presigned.txt"
        minio_client.put_object(
            test_bucket,
            object_name,
            io.BytesIO(test_data),
            len(test_data),
        )

        url = tos_client.get_presigned_get_url(
            object_name=object_name,
            bucket_name=test_bucket,
            expires=timedelta(hours=1),
            client=minio_client,
        )

        assert isinstance(url, str)
        assert test_bucket in url
        assert object_name in url

    def test_get_presigned_get_url_custom_expiry(self, minio_client, test_bucket):
        # Upload test data first
        test_data = b"test expiry data"
        object_name = "test-expiry.txt"
        minio_client.put_object(
            test_bucket,
            object_name,
            io.BytesIO(test_data),
            len(test_data),
        )

        url = tos_client.get_presigned_get_url(
            object_name=object_name,
            bucket_name=test_bucket,
            expires=timedelta(hours=2),
            client=minio_client,
        )

        assert isinstance(url, str)


class TestObjectRemoval:
    """Test object removal operations."""

    def test_remove_object_success(self, minio_client, test_bucket):
        # Upload test data first
        test_data = b"test removal data"
        object_name = "test-remove.txt"
        minio_client.put_object(
            test_bucket,
            object_name,
            io.BytesIO(test_data),
            len(test_data),
        )

        # Verify it exists
        obj = minio_client.get_object(test_bucket, object_name)
        obj.close()
        obj.release_conn()

        # Remove
        tos_client.remove_object(
            object_name=object_name,
            bucket_name=test_bucket,
            client=minio_client,
        )

        # Verify it's removed
        with pytest.raises(S3Error):
            minio_client.get_object(test_bucket, object_name)

    def test_remove_nonexistent_object(self, minio_client, test_bucket):
        # Removing non-existent object should not raise error (MinIO's behavior)
        tos_client.remove_object(
            object_name="nonexistent-to-remove.txt",
            bucket_name=test_bucket,
            client=minio_client,
        )
