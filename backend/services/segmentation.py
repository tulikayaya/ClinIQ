from __future__ import annotations
import os
import tempfile


def segment_tumor(nifti_bytes: bytes) -> str | None:
    """
    Run tumor segmentation on a T1-post NIfTI image.

    TODO: plug in your chosen model here (HD-GLIO, nnU-Net BraTS, etc.)
          The function should:
          1. Write nifti_bytes to a temp file
          2. Run model inference
          3. Save the binary mask to another temp file
          4. Return the mask file path

    The returned path is served back to the client as a download.
    Clean up temp files after the response is sent (use BackgroundTasks in the route).
    """
    raise NotImplementedError(
        "Segmentation model not yet configured. "
        "See services/segmentation.py to plug in HD-GLIO or nnU-Net."
    )
