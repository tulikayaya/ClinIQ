from __future__ import annotations
import io
from minio import Minio
from minio.error import S3Error
from config import settings

_client = Minio(
    settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=settings.minio_secure,
)


def _ensure_bucket():
    if not _client.bucket_exists(settings.minio_bucket):
        _client.make_bucket(settings.minio_bucket)


def upload_nifti(case_id: str, data: bytes) -> str:
    _ensure_bucket()
    object_name = f"{case_id}.nii.gz"
    _client.put_object(
        settings.minio_bucket,
        object_name,
        io.BytesIO(data),
        length=len(data),
        content_type="application/gzip",
    )
    return f"http://{settings.minio_endpoint}/{settings.minio_bucket}/{object_name}"


def get_nifti_bytes(case_id: str) -> bytes | None:
    object_name = f"{case_id}.nii.gz"
    try:
        response = _client.get_object(settings.minio_bucket, object_name)
        return response.read()
    except S3Error:
        # Try .nii as fallback
        try:
            object_name = f"{case_id}.nii"
            response = _client.get_object(settings.minio_bucket, object_name)
            return response.read()
        except S3Error:
            return None
