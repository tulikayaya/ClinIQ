# ClinIQ — Multimodal Clinical Case Retrieval for Neuro-Oncology

A multimodal RAG pipeline for brain tumor case retrieval. Given a natural language clinical query, ClinIQ returns the most similar historical cases ranked by combined radiomic image similarity and semantic clinical note similarity — surfacing matched scans, diagnoses, treatments, and outcomes.

---

## Dataset

**UCSD-PTGBM v1** — University of California San Diego Pediatric and Adult Glioblastoma dataset. Contains T1 post-contrast MRI scans with corresponding BraTS-format segmentation masks and structured clinical metadata across 92 patients (184 scan-mask pairs across multiple timepoints).

---

## Data Preparation

### 1. NIfTI Conversion and File Organization

Raw scans were downloaded from TCIA as DICOM archives and converted to NIfTI format (`.nii`) using `dcm2niix`. Scans and segmentation masks were organized into separate directories:

```
PKG - UCSD-PTGBM-v1/
    Images/     ← T1 post-contrast scans   (UCSD-PTGBM-XXXX_XX_T1post.nii)
    masks/      ← BraTS segmentation masks (UCSD-PTGBM-XXXX_XX_BraTS_tumor_seg.nii)
```

Scan-mask pairs were matched by extracting the case ID from each filename — the portion before the final underscore-delimited suffix — yielding 184 matched pairs across 92 patients.

### 2. Clinical Data Cleaning

Structured clinical metadata was provided as an Excel sheet (`UCSD_PTGBM-clinical-information_v3`). Since not all patients in the clinical sheet have corresponding imaging data, the clinical records were filtered to retain only cases for which a scan exists in the Images directory. This reduced the clinical dataset to match the 92 imaging subjects.

---

## Radiomic Feature Extraction

### Why Radiomics

Rather than using a black-box vision encoder to represent scans, we extract explicit quantitative features from the tumor region using **PyRadiomics**. This approach is:

- **Acquisition-independent** — shape and texture features are not affected by scanner brand or contrast dose
- **Interpretable** — every dimension of the vector has a clinical name and meaning
- **Training-free** — no labeled data or GPU required
- **Generalizable** — works with any segmentation mask source, including future automated segmenters

### Mask Preprocessing

BraTS segmentation masks use multiple integer labels to distinguish tumor subregions (necrotic core, edema, enhancing tumor). Rather than extracting features from a specific label, all non-zero voxels are collapsed into a single binary mask before extraction:

```python
binary_mask = (mask_data > 0).astype(np.uint8)
```

This makes the pipeline label-agnostic — compatible with any future segmentation model that outputs a binary mask, without requiring BraTS-specific label conventions.

### Feature Classes Selected

| Feature Class | What It Captures | Dimensions |
|---|---|---|
| **Shape** | Tumor geometry — volume, sphericity, elongation, surface area, compactness | ~14 |
| **GLCM** | Gray level co-occurrence texture — homogeneity, contrast, entropy, correlation | ~24 |
| **GLSZM** | Gray level size zone matrix — spatial scale of heterogeneity, zone uniformity | ~16 |

**Total: ~54 features per case**

### Why These Three, Why Not Others

**Kept:**
- **Shape** — captures gross morphology independent of intensity. Two tumors with similar shape profiles share geometric characteristics regardless of scanner settings.
- **GLCM** — captures spatial texture relationships between neighboring voxels. On T1 post-contrast, this reflects enhancement heterogeneity and internal tumor complexity.
- **GLSZM** — captures the scale of uniform regions inside the tumor. Complements GLCM by encoding how large or small the homogeneous patches are, not just how different they are.

**Dropped:**
- **First order** — purely intensity statistics (mean, variance, skewness). On T1 post-contrast, intensity is heavily influenced by scanner settings, contrast agent dose, injection timing, and patient weight — acquisition variables, not tumor biology. Too noisy for cross-patient similarity.
- **GLRLM** — run-length matrix features. Captures directional texture patterns but substantially overlaps with GLCM. With only 184 cases, adding redundant dimensions increases the curse of dimensionality without adding signal.

### Normalization

Raw radiomic features span wildly different scales — tumor volume in the hundreds of thousands, shape sphericity between 0 and 1. Without normalization, high-magnitude features dominate Euclidean distance calculations and make low-magnitude features irrelevant.

All features are normalized using **StandardScaler** (zero mean, unit variance) fitted on the full 184-case dataset. The fitted scaler is saved as `radiomic_scaler.pkl` and must be applied to any new scan before querying Qdrant, ensuring all vectors remain in the same scale space.

```
Raw features → StandardScaler (fitted once) → normalized vector → Qdrant
New scan     → same saved StandardScaler    → normalized vector → query
```

---

## Clinical Note Synthesis

### Why Synthesize Rather Than Embed Raw Fields

Embedding a raw Excel row directly produces poor vectors because the embedding model sees decontextualized numbers and abbreviations with no clinical meaning attached. The field value `412` means nothing without knowing it represents overall survival in days. The value `wildtype` means nothing without knowing it refers to IDH mutation status.

Converting structured fields to natural language first gives the embedding model the context it needs to produce clinically meaningful vectors.

### Template

The following fields are used to synthesize each clinical note:

```
Patient's Age, Sex at Birth, WHO 2021 Diagnosis (or Non-WHO 2021 if absent),
Grade, MGMT, IDH, 1p19q, ATRX,
Surgery (yes/no), Number of Surgeries, Surgery Extent,
Radiation (yes/no), Number of Radiation Courses,
1st Chemo Type
```

Missing fields are handled gracefully — if a field is absent or blank, the corresponding sentence is replaced with a clinical placeholder (e.g. "Surgical history unknown") rather than breaking or inserting "NaN".

**Example synthesized note:**
```
Patient is a 58 year old Male. WHO 2021 classification: Glioblastoma,
IDH Wildtype, Grade 4. Molecular profile: IDH wildtype, MGMT unmethylated,
1p19q intact, ATRX intact. The patient underwent 1 surgical procedure(s)
with extent of resection: GTR. Radiation therapy was administered over
1 course(s). First-line chemotherapy agent: Temozolomide.
```

Synthesized notes are stored in `synthesized_clinical_notes.xlsx` with one row per case ID.

---

## Embedding Strategy

### Model: MedCPT

Clinical notes and doctor queries are embedded using **MedCPT** (Medical Contrastive Pre-Training), a retrieval-optimized model trained on PubMed and clinical query-document pairs.

MedCPT uses **asymmetric encoding** — two separate encoders trained jointly in the same vector space:

| Encoder | Used For | HuggingFace ID |
|---|---|---|
| Article Encoder | Stored synthesized clinical notes (ingestion) | `ncats/MedCPT-Article-Encoder` |
| Query Encoder | Doctor's natural language queries (retrieval) | `ncats/MedCPT-Query-Encoder` |

**Why asymmetric encoding:**
Stored clinical notes are structured, comprehensive, and formal. Doctor queries are short, informal, and incomplete. Training separate encoders for each type produces better retrieval than forcing one model to handle both — the encoders are optimized to find each other across the format gap.

**Token limit:** 512 tokens per input. Synthesized notes average ~80 tokens. Doctor queries average ~40 tokens. The limit is not a constraint for this use case.

**Why not a general embedding model:**
General models (nomic-embed-text, text-embedding-3) understand clinical terminology but were not trained specifically for clinical retrieval tasks. MedCPT was trained on query-document pairs from the medical domain — its optimization objective directly matches this system's retrieval task.

---

## Vector Storage — Qdrant

Each case is stored as a single point in Qdrant with two named vectors and a metadata payload:

```json
{
  "id": "UCSD-PTGBM-0002_01",
  "vectors": {
    "radiomics": [0.23, -1.14, 0.87, ...],
    "clinical":  [0.45, 0.12, 0.98, ...]
  },
  "payload": {
    "case_id":   "UCSD-PTGBM-0002_01",
    "scan_path": "Images/UCSD-PTGBM-0002_01_T1post.nii",
    "diagnosis": "Glioblastoma IDH Wildtype",
    "grade":     "4",
    "treatment": "GTR + Temozolomide + Radiation",
    "survival":  "412 days"
  }
}
```

The `case_id` is the universal anchor — the same string used as the filename stem in Images, the row key in both Excel files, and the Qdrant point ID.

---

## Architecture

### Ingestion Pipeline

```
NIfTI scan + binary mask
        │
        ▼
PyRadiomics (shape + GLCM + GLSZM)
        │
        ▼
StandardScaler normalization
        │
        ▼
Radiomic vector (54-dim) ──────────────────────────┐
                                                    │
Excel clinical fields                               │
        │                                           │
        ▼                                           │
Synthesize natural language note                    │
        │                                           │
        ▼                                           │
MedCPT Article Encoder                              │
        │                                           │
        ▼                                           │
Clinical vector (768-dim) ─────────────────────────┤
                                                    │
                                                    ▼
                                         Qdrant point
                                         { radiomics vector,
                                           clinical vector,
                                           payload metadata }
```

### Retrieval Pipeline

```
Doctor types natural language query
        │
        ▼
MedCPT Query Encoder → clinical query vector (768-dim)
        │
        ▼
Qdrant hybrid search (named vector prefetch + RRF fusion)
        │
        ├── Search "radiomics" vector → top-20 radiomic candidates
        └── Search "clinical" vector  → top-20 clinical candidates
                        │
                        ▼
            Reciprocal Rank Fusion (RRF)
            rewards cases ranking highly in BOTH searches
                        │
                        ▼
                Top-k matched cases
                        │
                        ▼
        Return: scan image + diagnosis + treatment + outcome
```

### Why Hybrid Search + RRF

A case that is visually similar (high radiomic score) but clinically different (low clinical score) ranks lower than one that is similar on both dimensions. RRF does not require manual weighting — it rewards consistent performance across both vector spaces. This mirrors how a neuroradiologist actually searches: a tumor that looks alike AND was treated the same way is more useful than one that only satisfies one criterion.

---

## Stack

| Component | Tool | Why |
|---|---|---|
| Feature extraction | PyRadiomics | Explicit, interpretable, training-free |
| Normalization | scikit-learn StandardScaler | Scale-invariant distance calculation |
| Clinical embedding | MedCPT (HuggingFace) | Retrieval-optimized, clinical domain |
| Vector database | Qdrant | Native named vectors, payload filtering, RRF fusion |
| LLM inference | Ollama (Llama3 / Meditron) | Self-hosted, no data leaves network |
| Image storage | MinIO | Self-hosted S3-compatible object storage |

**Fully self-hosted** — no third-party APIs in the retrieval pipeline. All inference runs on local hardware.

---

## Research Scope

This project evaluates three retrieval paradigms for brain tumor case similarity:

| Case | Retrieval Signal | Embedding |
|---|---|---|
| Case 1 | Clinical notes only | MedCPT text vectors |
| Case 2 | Vision-language model | Nemotron embed VL joint vectors |
| Case 3 | Radiomics + clinical notes | PyRadiomics + MedCPT hybrid (this implementation) |

Evaluation metric: clinician-rated relevance of top-3 retrieved cases per query, compared across all three paradigms.
