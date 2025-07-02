// Smartscripts/frontend/src/components/ReviewPanel.js
import React, { useState, useEffect } from "react";

const ReviewPanel = ({ reviewItems = [], onSave }) => {
  const [items, setItems] = useState([]);

  useEffect(() => {
    setItems(reviewItems);
  }, [reviewItems]);

  const handleScoreChange = (index, value) => {
    const updated = [...items];
    updated[index].score = parseFloat(value);
    setItems(updated);
  };

  const handleFeedbackChange = (index, value) => {
    const updated = [...items];
    updated[index].feedback = value;
    setItems(updated);
  };

  const handleOverrideToggle = (index) => {
    const updated = [...items];
    updated[index].override = !updated[index].override;
    setItems(updated);
  };

  const saveChanges = () => {
    if (onSave) onSave(items);
  };

  return (
    <div className="review-panel p-3 border rounded">
      <h3>Manual Review</h3>
      {items.length === 0 && <p>No review items available.</p>}
      {items.map((item, idx) => (
        <div key={idx} className="mb-3 p-2 border rounded">
          <div>
            <strong>Question {item.number || idx + 1}:</strong> {item.question || "N/A"}
          </div>
          <div>
            <label>Your Score: </label>
            <input
              type="number"
              min="0"
              max={item.max_score || 1}
              step="0.1"
              value={item.score || 0}
              onChange={(e) => handleScoreChange(idx, e.target.value)}
              disabled={!item.override}
            />
            <span> / {item.max_score}</span>
          </div>
          <div>
            <label>Feedback:</label><br />
            <textarea
              rows="3"
              value={item.feedback || ""}
              onChange={(e) => handleFeedbackChange(idx, e.target.value)}
              disabled={!item.override}
            />
          </div>
          <div>
            <label>
              <input
                type="checkbox"
                checked={item.override || false}
                onChange={() => handleOverrideToggle(idx)}
              />
              {" "}Manual Override
            </label>
          </div>
        </div>
      ))}
      <button onClick={saveChanges} className="btn btn-primary mt-2">
        Save Changes
      </button>
    </div>
  );
};

export default ReviewPanel;
