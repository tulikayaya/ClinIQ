import { useState, useEffect } from "react";
import { getSlices } from "../api/client";
import { useGallery } from "../context/GalleryContext";

const PLANES = ["axial", "coronal", "sagittal"];

export default function ImageSlices({ caseId }) {
  const [slices, setSlices] = useState(null);
  const [error, setError]   = useState(false);
  const { registerImages, openAt } = useGallery();

  useEffect(() => {
    if (!caseId) return;
    getSlices(caseId)
      .then(data => {
        setSlices(data);
        registerImages(caseId, PLANES.map(plane => ({
          src:   `data:image/png;base64,${data[plane]}`,
          label: `${caseId} — ${plane}`,
        })));
      })
      .catch(() => setError(true));
  }, [caseId]);

  if (error)   return <p className="slice-error">Image unavailable</p>;
  if (!slices) return <p className="slice-loading">Loading slices…</p>;

  return (
    <div className="image-slices">
      {PLANES.map((plane, i) => (
        <div key={plane} className="slice-wrap">
          <span className="slice-label">{plane}</span>
          <img
            src={`data:image/png;base64,${slices[plane]}`}
            alt={`${plane} slice of ${caseId}`}
            className="slice-thumb"
            onClick={() => openAt(caseId, i)}
          />
        </div>
      ))}
    </div>
  );
}
