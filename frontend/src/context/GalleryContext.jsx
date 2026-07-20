import { createContext, useContext, useState, useCallback, useRef } from "react";

const GalleryCtx = createContext(null);

export function GalleryProvider({ children }) {
  const [state, setState] = useState({ open: false, images: [], index: 0 });
  const registry = useRef(new Map()); // caseId → [{src, label}, ...], preserves insertion order

  const registerImages = useCallback((caseId, images) => {
    registry.current.set(caseId, images);
  }, []);

  const openAt = useCallback((caseId, localIndex) => {
    const all = [];
    let startIdx = 0;
    let found = false;
    for (const [id, imgs] of registry.current) {
      if (id === caseId && !found) {
        startIdx = all.length + localIndex;
        found = true;
      }
      all.push(...imgs);
    }
    setState({ open: true, images: all, index: startIdx });
  }, []);

  const close = useCallback(() => setState(s => ({ ...s, open: false })), []);
  const prev  = useCallback(() => setState(s => ({ ...s, index: (s.index - 1 + s.images.length) % s.images.length })), []);
  const next  = useCallback(() => setState(s => ({ ...s, index: (s.index + 1) % s.images.length })), []);

  return (
    <GalleryCtx.Provider value={{ registerImages, openAt, close, prev, next, ...state }}>
      {children}
    </GalleryCtx.Provider>
  );
}

export const useGallery = () => useContext(GalleryCtx);
