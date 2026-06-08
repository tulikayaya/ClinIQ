import { useState } from "react";
import { uploadCase } from "../api/client";

const INITIAL = {
  age: "", sex: "", diagnosis: "", grade: "",
  idh: "", mgmt: "", codeletion: "", atrx: "",
  surgery: "", radiation: "", chemo: "", extra_notes: "",
};

export default function UploadForm() {
  const [fields, setFields]   = useState(INITIAL);
  const [image, setImage]     = useState(null);
  const [mask, setMask]       = useState(null);
  const [status, setStatus]   = useState("");
  const [loading, setLoading] = useState(false);

  function handleField(e) {
    setFields({ ...fields, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!image || !mask) {
      setStatus("Please attach both a NIfTI image and a mask.");
      return;
    }
    setLoading(true);
    setStatus("");
    try {
      const result = await uploadCase(image, mask, fields);
      setStatus(`✓ Case "${result.case_id}" uploaded successfully.`);
      setFields(INITIAL);
      setImage(null);
      setMask(null);
    } catch {
      setStatus("Upload failed. Check that all fields are filled and files are valid.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="upload-form" onSubmit={handleSubmit}>
      <div className="form-row">
        <label>T1-post NIfTI *
          <input type="file" accept=".nii,.nii.gz" onChange={(e) => setImage(e.target.files[0])} required />
        </label>
        <label>Tumor Mask *
          <input type="file" accept=".nii,.nii.gz" onChange={(e) => setMask(e.target.files[0])} required />
        </label>
      </div>

      <fieldset>
        <legend>Patient Demographics</legend>
        <div className="form-row">
          <label>Age *      <input name="age"       value={fields.age}       onChange={handleField} required /></label>
          <label>Sex *      <input name="sex"       value={fields.sex}       onChange={handleField} required /></label>
          <label>Grade *    <input name="grade"     value={fields.grade}     onChange={handleField} required /></label>
        </div>
      </fieldset>

      <fieldset>
        <legend>Diagnosis</legend>
        <label>Primary Diagnosis *
          <input name="diagnosis" value={fields.diagnosis} onChange={handleField} required />
        </label>
      </fieldset>

      <fieldset>
        <legend>Molecular Markers</legend>
        <div className="form-row">
          <label>IDH *         <input name="idh"        value={fields.idh}        onChange={handleField} required /></label>
          <label>MGMT *        <input name="mgmt"       value={fields.mgmt}       onChange={handleField} required /></label>
          <label>1p19q *       <input name="codeletion" value={fields.codeletion} onChange={handleField} required /></label>
          <label>ATRX *        <input name="atrx"       value={fields.atrx}       onChange={handleField} required /></label>
        </div>
      </fieldset>

      <fieldset>
        <legend>Treatment</legend>
        <div className="form-row">
          <label>Surgery *    <input name="surgery"   value={fields.surgery}   onChange={handleField} required /></label>
          <label>Radiation *  <input name="radiation" value={fields.radiation} onChange={handleField} required /></label>
          <label>Chemo *      <input name="chemo"     value={fields.chemo}     onChange={handleField} required /></label>
        </div>
      </fieldset>

      <label>Additional Notes
        <textarea name="extra_notes" value={fields.extra_notes} onChange={handleField} rows={3} />
      </label>

      {status && <p className="upload-status">{status}</p>}

      <button type="submit" disabled={loading}>
        {loading ? "Uploading…" : "Upload Case"}
      </button>
    </form>
  );
}
