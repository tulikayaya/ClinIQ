from __future__ import annotations
import io
import os
import shutil
import tempfile
import zipfile

import SimpleITK as sitk


def _find_series(root: str) -> tuple[str, list[str]]:
    """Walk root to find the first directory containing a DICOM series."""
    for dirpath, _, _ in os.walk(root):
        series_ids = sitk.ImageSeriesReader.GetGDCMSeriesIDs(dirpath)
        if series_ids:
            return dirpath, list(series_ids)
    return root, []


def convert_dicom_to_nifti(zip_bytes: bytes) -> tuple[str, str] | None:
    """
    Unzip a DICOM archive, convert with SimpleITK, return (output_path, work_dir).
    Caller must schedule cleanup of work_dir (e.g. via BackgroundTask).
    On failure: cleans up work_dir internally and returns None.
    """
    work_dir = tempfile.mkdtemp()
    try:
        dicom_dir = os.path.join(work_dir, "dicoms")
        os.makedirs(dicom_dir)
        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as z:
            z.extractall(dicom_dir)

        reader = sitk.ImageSeriesReader()
        series_dir, series_ids = _find_series(dicom_dir)
        if not series_ids:
            raise ValueError("No DICOM series found in archive")

        dicom_names = reader.GetGDCMSeriesFileNames(series_dir, series_ids[0])
        reader.SetFileNames(dicom_names)
        image = reader.Execute()

        out_dir = os.path.join(work_dir, "nifti")
        os.makedirs(out_dir)
        output_path = os.path.join(out_dir, "converted.nii.gz")
        sitk.WriteImage(image, output_path)

        return output_path, work_dir

    except Exception as e:
        print(f"DICOM conversion error: {e}")
        shutil.rmtree(work_dir, ignore_errors=True)
        return None
