from __future__ import annotations
import os
import shutil
import subprocess
import tempfile
import zipfile


def convert_dicom_to_nifti(zip_bytes: bytes) -> str | None:
    """
    Unzip a DICOM archive, run dcm2niix, return path to the output .nii.gz.
    Requires dcm2niix to be installed and on PATH.
    """
    work_dir = tempfile.mkdtemp()
    try:
        zip_path = os.path.join(work_dir, "input.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_bytes)

        dicom_dir = os.path.join(work_dir, "dicoms")
        os.makedirs(dicom_dir)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(dicom_dir)

        out_dir = os.path.join(work_dir, "nifti")
        os.makedirs(out_dir)

        result = subprocess.run(
            ["dcm2niix", "-z", "y", "-o", out_dir, dicom_dir],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"dcm2niix error:\n{result.stderr}")
            return None

        nifti_files = [f for f in os.listdir(out_dir) if f.endswith(".nii.gz")]
        if not nifti_files:
            return None

        return os.path.join(out_dir, nifti_files[0])

    except Exception as e:
        print(f"DICOM conversion error: {e}")
        shutil.rmtree(work_dir, ignore_errors=True)
        return None
