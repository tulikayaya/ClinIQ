from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from services.segmentation import segment_tumor

router = APIRouter()


@router.post("")
async def segment(file: UploadFile = File(...)):
    """
    Accept a T1-post .nii or .nii.gz, run tumor segmentation,
    return the binary mask .nii.gz for download.
    """
    if not (file.filename.endswith(".nii") or file.filename.endswith(".nii.gz")):
        raise HTTPException(status_code=400, detail="Upload a .nii or .nii.gz file.")

    nifti_bytes = await file.read()
    mask_path = segment_tumor(nifti_bytes)

    if mask_path is None:
        raise HTTPException(status_code=500, detail="Segmentation failed.")

    return FileResponse(
        path=mask_path,
        media_type="application/gzip",
        filename="tumor_mask.nii.gz",
    )
