import { useState, useRef } from "react";
import { extractFeatures } from "../api/client";

export default function ChatInput({ onSend, disabled }) {
  const [text, setText]         = useState("");
  const [image, setImage]       = useState(null);
  const [mask, setMask]         = useState(null);
  const [extracting, setExtr]   = useState(false);
  const imageRef                = useRef();
  const maskRef                 = useRef();

  async function handleSend() {
    if (!text.trim() && !image) return;

    let vector = null;

    // If both image and mask are attached, extract features before sending
    if (image && mask) {
      setExtr(true);
      try {
        const data = await extractFeatures(image, mask);
        vector = data.vector;
      } catch {
        alert("Feature extraction failed. Check that the image and mask are valid NIfTI files.");
        setExtr(false);
        return;
      }
      setExtr(false);
    }

    onSend(text, vector);
    setText("");
    setImage(null);
    setMask(null);
    if (imageRef.current) imageRef.current.value = "";
    if (maskRef.current)  maskRef.current.value  = "";
  }

  function handleKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="chat-input-area">
      <div className="file-attachments">
        <label>
          T1-post .nii
          <input
            ref={imageRef}
            type="file"
            accept=".nii,.nii.gz"
            onChange={(e) => setImage(e.target.files[0])}
          />
        </label>
        <label>
          Mask .nii
          <input
            ref={maskRef}
            type="file"
            accept=".nii,.nii.gz"
            onChange={(e) => setMask(e.target.files[0])}
          />
        </label>
        {image && <span className="attach-badge">📎 {image.name}</span>}
        {mask  && <span className="attach-badge">🩻 {mask.name}</span>}
      </div>

      <div className="text-row">
        <textarea
          placeholder="Describe the patient or ask a question..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKey}
          rows={3}
          disabled={disabled || extracting}
        />
        <button
          onClick={handleSend}
          disabled={disabled || extracting || (!text.trim() && !image)}
        >
          {extracting ? "Extracting..." : "Send"}
        </button>
      </div>
    </div>
  );
}
