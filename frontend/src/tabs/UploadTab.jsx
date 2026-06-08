import UploadForm from "../components/UploadForm";

export default function UploadTab() {
  return (
    <div className="upload-tab">
      <h2>Upload a New Case</h2>
      <p className="upload-description">
        Submit a new patient case to the database. Provide the T1-post NIfTI
        image, tumor mask, and clinical information. The case will be ingested
        and made available for future retrievals.
      </p>
      <UploadForm />
    </div>
  );
}
