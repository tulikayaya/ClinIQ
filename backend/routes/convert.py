from __future__ import annotations
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from services.dicom_converter import convert_dicom_to_nifti

router = APIRouter()

ZIP_MAGIC = b'PK\x03\x04'


@router.post("/dicom")
async def convert_dicom(file: UploadFile = File(...)):
    """
    Accept a ZIP of DICOM files, convert to NIfTI with SimpleITK,
    return converted.nii.gz for download. Temp dir is cleaned up after response.
    """
    zip_bytes = await file.read()

    if len(zip_bytes) < 4 or zip_bytes[:4] != ZIP_MAGIC:
        raise HTTPException(
            status_code=400,
            detail="File is not a valid ZIP archive. Upload a .zip of DICOM files.",
        )

    result = convert_dicom_to_nifti(zip_bytes)
    if result is None:
        raise HTTPException(status_code=500, detail="DICOM conversion failed.")

    output_path, work_dir = result
    return FileResponse(
        path=output_path,
        media_type="application/gzip",
        filename="converted.nii.gz",
        background=BackgroundTask(shutil.rmtree, work_dir, ignore_errors=True),
    )
