import { useState } from "react";
import { segmentTumor } from "../api/client";

export default function MaskSegmenter() {
  const [file, setFile]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  async function handleSegment() {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const blob = await segmentTumor(file);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "tumor_mask.nii.gz";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError("Segmentation failed. Model may not be configured yet.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="tool-widget">
      <input
        type="file"
        accept=".nii,.nii.gz"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button onClick={handleSegment} disabled={!file || loading}>
        {loading ? "Segmenting..." : "Extract Mask & Download"}
      </button>
      {error && <p className="error">{error}</p>}
    </div>
  );
}
