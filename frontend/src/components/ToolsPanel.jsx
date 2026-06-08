import { useState } from "react";
import DicomConverter from "./DicomConverter";
import MaskSegmenter from "./MaskSegmenter";

export default function ToolsPanel() {
  const [open, setOpen] = useState(true);

  return (
    <aside className={`tools-panel ${open ? "expanded" : "collapsed"}`}>
      <button className="tools-toggle" onClick={() => setOpen(!open)}>
        {open ? "◀ Tools" : "▶"}
      </button>

      {open && (
        <div className="tools-content">
          <section className="tool-section">
            <h3>DICOM → NIfTI</h3>
            <p>Upload a .zip of DICOM files to convert to NIfTI format.</p>
            <DicomConverter />
          </section>

          <section className="tool-section">
            <h3>Tumor Mask</h3>
            <p>Upload a T1-post .nii to extract the tumor segmentation mask.</p>
            <MaskSegmenter />
          </section>
        </div>
      )}
    </aside>
  );
}
