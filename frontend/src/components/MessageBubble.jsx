import CaseCard from "./CaseCard";

export default function MessageBubble({ role, content, cases = [] }) {
  return (
    <div className={`bubble ${role}`}>
      <div className="bubble-text">{content}</div>
      {cases.length > 0 && (
        <div className="case-list">
          {cases.map((c) => (
            <CaseCard
              key={c.case_id}
              caseId={c.case_id}
              note={c.note}
              score={c.score}
            />
          ))}
        </div>
      )}
    </div>
  );
}
