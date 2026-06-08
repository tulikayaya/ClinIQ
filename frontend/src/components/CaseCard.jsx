import ImageSlices from "./ImageSlices";

export default function CaseCard({ caseId, note, score }) {
  return (
    <div className="case-card">
      <div className="case-header">
        <span className="case-id">{caseId}</span>
        {score !== undefined && (
          <span className="case-score">Score: {score.toFixed(3)}</span>
        )}
      </div>

      <ImageSlices caseId={caseId} />

      <p className="case-note">{note}</p>
    </div>
  );
}
