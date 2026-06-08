from __future__ import annotations
import io
import os
import pickle
import tempfile
import numpy as np
import nibabel as nib
from radiomics import featureextractor
from config import settings

_scaler = None
_extractor = None


def _load():
    global _scaler, _extractor
    if _scaler is None:
        with open(settings.scaler_path, "rb") as f:
            _scaler = pickle.load(f)

    if _extractor is None:
        _extractor = featureextractor.RadiomicsFeatureExtractor()
        _extractor.disableAllFeatures()
        _extractor.enableFeatureClassByName("shape")
        _extractor.enableFeatureClassByName("glcm")
        _extractor.enableFeatureClassByName("glszm")


def _save_temp_nifti(data: bytes) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".nii", delete=False)
    tmp.write(data)
    tmp.flush()
    return tmp.name


def extract_features(image_bytes: bytes, mask_bytes: bytes) -> list[float] | None:
    _load()

    image_path = mask_path = None
    try:
        image_path = _save_temp_nifti(image_bytes)

        # Binarize mask — nibabel needs a real file path, not BytesIO
        raw_mask_path = _save_temp_nifti(mask_bytes)
        mask_img = nib.load(raw_mask_path)
        binary = (mask_img.get_fdata() > 0).astype(np.uint8)
        tmp_mask = tempfile.NamedTemporaryFile(suffix=".nii", delete=False)
        nib.save(nib.Nifti1Image(binary, mask_img.affine), tmp_mask.name)
        os.unlink(raw_mask_path)
        mask_path = tmp_mask.name

        feature_dict = _extractor.execute(image_path, mask_path)
        raw = [
            float(v)
            for k, v in feature_dict.items()
            if k.startswith("original_") and not isinstance(v, str)
        ]

        normalized = _scaler.transform([raw])[0].tolist()
        return normalized

    except Exception as e:
        print(f"Feature extraction error: {e}")
        return None

    finally:
        for p in [image_path, mask_path]:
            if p:
                try:
                    os.unlink(p)
                except Exception:
                    pass
