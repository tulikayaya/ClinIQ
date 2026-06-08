const BASE = "";   // Vite proxy forwards to http://localhost:8000

async function post(path, body) {
  const res = await fetch(BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function postForm(path, formData) {
  const res = await fetch(BASE + path, { method: "POST", body: formData });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function postFormBlob(path, formData) {
  const res = await fetch(BASE + path, { method: "POST", body: formData });
  if (!res.ok) throw new Error(await res.text());
  return res.blob();
}

// ── Chat ──────────────────────────────────────────────────────
export function sendMessage(messages, radiomic_vector = null) {
  return post("/chat", { messages, radiomic_vector });
}

// ── Retrieval ─────────────────────────────────────────────────
export function retrieveByClinical(note, top_k = 5) {
  return post("/retrieve/clinical", { note, top_k });
}

export function retrieveByRadiomics(vector, top_k = 5) {
  return post("/retrieve/radiomics", { vector, top_k });
}

export function retrieveCombined(note, vector, top_k = 5) {
  return post("/retrieve/combined", { note, vector, top_k });
}

// ── Image slices ──────────────────────────────────────────────
export function getSlices(caseId) {
  return fetch(`${BASE}/images/${caseId}/slices`).then((r) => {
    if (!r.ok) throw new Error(r.statusText);
    return r.json();
  });
}

// ── DICOM converter ───────────────────────────────────────────
export function convertDicom(zipFile) {
  const fd = new FormData();
  fd.append("file", zipFile);
  return postFormBlob("/convert/dicom", fd);
}

// ── Tumor segmentation ────────────────────────────────────────
export function segmentTumor(niftiFile) {
  const fd = new FormData();
  fd.append("file", niftiFile);
  return postFormBlob("/segment", fd);
}

// ── Feature extraction ────────────────────────────────────────
export function extractFeatures(imageFile, maskFile) {
  const fd = new FormData();
  fd.append("image", imageFile);
  fd.append("mask",  maskFile);
  return postForm("/features", fd);
}

// ── Upload new case ───────────────────────────────────────────
export function uploadCase(imageFile, maskFile, fields) {
  const fd = new FormData();
  fd.append("image", imageFile);
  fd.append("mask",  maskFile);
  Object.entries(fields).forEach(([k, v]) => fd.append(k, v));
  return postForm("/upload", fd);
}
