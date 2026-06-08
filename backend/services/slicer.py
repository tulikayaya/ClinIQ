from __future__ import annotations
import io
import os
import base64
import tempfile
import numpy as np
import nibabel as nib
from PIL import Image


def _normalize_slice(arr: np.ndarray) -> np.ndarray:
    mn, mx = arr.min(), arr.max()
    if mx == mn:
        return np.zeros_like(arr, dtype=np.uint8)
    return ((arr - mn) / (mx - mn) * 255).astype(np.uint8)


def _slice_to_base64(arr: np.ndarray) -> str:
    img = Image.fromarray(_normalize_slice(arr))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def extract_slices(nifti_bytes: bytes) -> dict[str, str]:
    """
    Load a NIfTI from bytes, extract center axial/coronal/sagittal slices,
    return as base64-encoded PNG strings.
    """
    # Detect whether bytes are gzip-compressed to pick the right extension
    suffix = ".nii.gz" if nifti_bytes[:2] == b"\x1f\x8b" else ".nii"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(nifti_bytes)
            tmp_path = tmp.name
        img = nib.load(tmp_path)
        data = img.get_fdata()
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
    x, y, z = data.shape[0] // 2, data.shape[1] // 2, data.shape[2] // 2

    return {
        "axial":    _slice_to_base64(np.rot90(data[:, :, z])),
        "coronal":  _slice_to_base64(np.rot90(data[:, y, :])),
        "sagittal": _slice_to_base64(np.rot90(data[x, :, :])),
    }
