from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from services.dicom_converter import convert_dicom_to_nifti
import tempfile, os

router = APIRouter()


@router.post("/dicom")
async def convert_dicom(file: UploadFile = File(...)):
    """
    Accept a zip of DICOM files, convert to NIfTI via dcm2niix,
    return the .nii.gz for download.
    """
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Upload a .zip of DICOM files.")

    zip_bytes = await file.read()
    output_path = convert_dicom_to_nifti(zip_bytes)

    if output_path is None:
        raise HTTPException(status_code=500, detail="Conversion failed.")

    return FileResponse(
        path=output_path,
        media_type="application/gzip",
        filename="converted.nii.gz",
    )
