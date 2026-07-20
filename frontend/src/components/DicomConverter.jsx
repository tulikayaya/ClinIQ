import { useState } from "react";
import { convertDicom } from "../api/client";

export default function DicomConverter() {
  const [file, setFile]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  async function handleConvert() {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const blob = await convertDicom(file);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "converted.nii.gz";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e.message || "Conversion failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="tool-widget">
      <input
        type="file"
        accept=".zip"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button onClick={handleConvert} disabled={!file || loading}>
        {loading ? "Converting..." : "Convert & Download"}
      </button>
      {error && <p className="error">{error}</p>}
    </div>
  );
}
