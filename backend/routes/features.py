from fastapi import APIRouter, UploadFile, File, HTTPException
from services.radiomics import extract_features

router = APIRouter()


@router.post("")
async def get_features(
    image: UploadFile = File(...),
    mask:  UploadFile = File(...),
):
    """
    Accept a .nii image and .nii mask, extract PyRadiomics features,
    normalize with the saved scaler, return the 54-dim vector.
    """
    image_bytes = await image.read()
    mask_bytes  = await mask.read()

    vector = extract_features(image_bytes, mask_bytes)

    if vector is None:
        raise HTTPException(status_code=500, detail="Feature extraction failed.")

    return {"vector": vector, "dim": len(vector)}
