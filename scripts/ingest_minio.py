"""
One-time script: upload the 184 existing .nii images to MinIO,
then patch each Qdrant point's payload with the resulting image_url.

Run from the ClinIQ root:
    python scripts/ingest_minio.py
"""

from pathlib import Path
import urllib3
from minio import Minio
from qdrant_client import QdrantClient
from qdrant_client.models import SetPayload

# ── Config ──────────────────────────────────────────────────────
IMAGE_DIR   = Path(r"C:\Users\cutet\Downloads\PKG - UCSD-PTGBM-v1\Images")
BUCKET      = "cliniq-images"
COLLECTION  = "cliniq_cases"

# 5-minute timeout to handle large 64 MB files
_http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=10, read=300))
minio_client  = Minio("localhost:9000", access_key="minioadmin", secret_key="minioadmin", secure=False, http_client=_http)
qdrant_client = QdrantClient(host="localhost", port=6333)

import hashlib

def case_id_from_filename(stem: str) -> str:
    # UCSD-PTGBM-0002_01_T1post → UCSD-PTGBM-0002_01
    return stem.rsplit("_", 1)[0]

def point_id(case_id: str) -> int:
    return int(hashlib.sha256(case_id.encode()).hexdigest(), 16) % (10**15)


def ensure_bucket():
    if not minio_client.bucket_exists(BUCKET):
        minio_client.make_bucket(BUCKET)
        print(f"Created bucket: {BUCKET}")


def upload_and_patch(nii_path: Path) -> None:
    case_id = case_id_from_filename(nii_path.stem)
    object_name = f"{case_id}.nii"

    # Upload to MinIO
    minio_client.fput_object(
        BUCKET,
        object_name,
        str(nii_path),
        content_type="application/octet-stream",
    )
    image_url = f"http://localhost:9000/{BUCKET}/{object_name}"

    # Patch Qdrant payload
    pid = point_id(case_id)
    qdrant_client.set_payload(
        collection_name=COLLECTION,
        payload={"image_url": image_url},
        points=[pid],
    )
    print(f"  ✓ {case_id}  →  {image_url}")


RETRY_ONLY = [
    'UCSD-PTGBM-0029_01_T1post.nii', 'UCSD-PTGBM-0031_01_T1post.nii',
    'UCSD-PTGBM-0062_01_T1post.nii', 'UCSD-PTGBM-0094_01_T1post.nii',
    'UCSD-PTGBM-0107_01_T1post.nii', 'UCSD-PTGBM-0118_01_T1post.nii',
    'UCSD-PTGBM-0119_02_T1post.nii', 'UCSD-PTGBM-0128_01_T1post.nii',
    'UCSD-PTGBM-0165_01_T1post.nii', 'UCSD-PTGBM-0167_01_T1post.nii',
]

if __name__ == "__main__":
    ensure_bucket()

    # nii_files = list(IMAGE_DIR.glob("*.nii"))          # full run (all 184)
    # print(f"Found {len(nii_files)} .nii files in {IMAGE_DIR}\n")

    nii_files = [IMAGE_DIR / name for name in RETRY_ONLY]  # retry failed only
    print(f"Retrying {len(nii_files)} failed files with extended timeout...\n")

    failed = []
    for f in sorted(nii_files):
        try:
            upload_and_patch(f)
        except Exception as e:
            print(f"  ✗ {f.name} — {e}")
            failed.append(f.name)

    print(f"\nDone.  Uploaded: {len(nii_files) - len(failed)}  Failed: {len(failed)}")
    if failed:
        print("Failed files:", failed)
