import { useState, useEffect } from "react";
import { getSlices } from "../api/client";

export default function ImageSlices({ caseId }) {
  const [slices, setSlices] = useState(null);
  const [error, setError]   = useState(false);

  useEffect(() => {
    if (!caseId) return;
    getSlices(caseId)
      .then(setSlices)
      .catch(() => setError(true));
  }, [caseId]);

  if (error)   return <p className="slice-error">Image unavailable</p>;
  if (!slices) return <p className="slice-loading">Loading slices…</p>;

  return (
    <div className="image-slices">
      {["axial", "coronal", "sagittal"].map((plane) => (
        <div key={plane} className="slice-wrap">
          <span className="slice-label">{plane}</span>
          <img
            src={`data:image/png;base64,${slices[plane]}`}
            alt={`${plane} slice of ${caseId}`}
          />
        </div>
      ))}
    </div>
  );
}
