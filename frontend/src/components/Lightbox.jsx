import { useEffect } from "react";
import { createPortal } from "react-dom";
import { useGallery } from "../context/GalleryContext";

export default function Lightbox() {
  const { open, images, index, close, prev, next } = useGallery();

  useEffect(() => {
    if (!open) return;
    function onKey(e) {
      if (e.key === "Escape")     close();
      if (e.key === "ArrowLeft")  prev();
      if (e.key === "ArrowRight") next();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, close, prev, next]);

  if (!open || images.length === 0) return null;

  const current = images[index];

  return createPortal(
    <div className="lb-backdrop" onClick={close}>
      <button
        className="lb-arrow lb-prev"
        onClick={e => { e.stopPropagation(); prev(); }}
        aria-label="Previous image"
      >
        &#8592;
      </button>

      <div className="lb-content" onClick={e => e.stopPropagation()}>
        <img className="lb-img" src={current.src} alt={current.label} />
        <div className="lb-meta">
          <span className="lb-label">{current.label}</span>
          <span className="lb-counter">{index + 1} / {images.length}</span>
        </div>
      </div>

      <button
        className="lb-arrow lb-next"
        onClick={e => { e.stopPropagation(); next(); }}
        aria-label="Next image"
      >
        &#8594;
      </button>

      <button className="lb-close" onClick={close} aria-label="Close">&#x2715;</button>
    </div>,
    document.body,
  );
}
