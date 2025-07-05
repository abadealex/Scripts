import React, { useState, useEffect } from "react";
import api from "../services/api";

function TeacherReviewPage({ submissionId }) {
  const [text, setText] = useState("");
  const [confidence, setConfidence] = useState(1);
  const [needsReview, setNeedsReview] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.post("/review_script", { submission_id: submissionId }).then(({ data }) => {
      setText(data.extracted_text);
      setConfidence(data.confidence);
      setNeedsReview(data.needs_human_review);
      setLoading(false);
    });
  }, [submissionId]);

  const handleSave = () => {
    setSaving(true);
    api.post("/submit_review", {
      submission_id: submissionId,
      corrected_text: text,
      manual_override: true,
    }).then(() => {
      setSaving(false);
      alert("Saved successfully!");
    });
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Review Script</h2>
      <p>Confidence: {(confidence * 100).toFixed(1)}%</p>
      {needsReview ? (
        <textarea
          rows={15}
          cols={80}
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
      ) : (
        <pre>{text}</pre>
      )}
      {needsReview && (
        <button onClick={handleSave} disabled={saving}>
          {saving ? "Saving..." : "Submit Correction"}
        </button>
      )}
    </div>
  );
}

export default TeacherReviewPage;
