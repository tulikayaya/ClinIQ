from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from services.minio import upload_nifti
from services.radiomics import extract_features
from services.embedder import embed_note
from services.qdrant import upsert_point
import hashlib

router = APIRouter()


@router.post("")
async def upload_case(
    image:      UploadFile = File(...),
    mask:       UploadFile = File(...),
    age:        str = Form(...),
    sex:        str = Form(...),
    diagnosis:  str = Form(...),
    grade:      str = Form(...),
    idh:        str = Form(...),
    mgmt:       str = Form(...),
    codeletion: str = Form(...),
    atrx:       str = Form(...),
    surgery:    str = Form(...),
    radiation:  str = Form(...),
    chemo:      str = Form(...),
    extra_notes: Optional[str] = Form(default=""),
):
    """
    Full ingest pipeline for a new case:
    1. Upload .nii to MinIO
    2. Extract radiomic features
    3. Synthesize + embed clinical note
    4. Upsert into Qdrant
    """
    image_bytes = await image.read()
    mask_bytes  = await mask.read()

    # Build a case ID from the filename (strip extension)
    case_id = image.filename.replace(".nii.gz", "").replace(".nii", "")

    # 1. Upload to MinIO
    image_url = upload_nifti(case_id, image_bytes)

    # 2. Extract radiomic features
    vector = extract_features(image_bytes, mask_bytes)
    if vector is None:
        raise HTTPException(status_code=500, detail="Feature extraction failed.")

    # 3. Synthesize note
    note = (
        f"Patient is a {age} year old {sex}. "
        f"Primary diagnosis: {diagnosis}, Grade {grade}. "
        f"Molecular profile: IDH {idh}, MGMT {mgmt}, 1p19q {codeletion}, ATRX {atrx}. "
        f"Surgery: {surgery}. Radiation: {radiation}. "
        f"First-line chemotherapy: {chemo}."
    )
    if extra_notes:
        note += f" Additional notes: {extra_notes}"

    clinical_vector = embed_note(note)

    # 4. Upsert into Qdrant
    point_id = int(hashlib.sha256(case_id.encode()).hexdigest(), 16) % (10**15)
    upsert_point(point_id, case_id, note, vector, clinical_vector, image_url)

    return {"status": "ok", "case_id": case_id, "image_url": image_url}
