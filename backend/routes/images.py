from fastapi import APIRouter, HTTPException
from services.minio import get_nifti_bytes
from services.slicer import extract_slices

router = APIRouter()


@router.get("/{case_id}/slices")
def get_slices(case_id: str):
    """
    Fetch the NIfTI for case_id from MinIO, extract center
    axial / coronal / sagittal slices, return as base64 PNGs.
    """
    nifti_bytes = get_nifti_bytes(case_id)
    if nifti_bytes is None:
        raise HTTPException(status_code=404, detail=f"No image found for {case_id}")

    slices = extract_slices(nifti_bytes)
    return {
        "case_id": case_id,
        "axial":    slices["axial"],
        "coronal":  slices["coronal"],
        "sagittal": slices["sagittal"],
    }
