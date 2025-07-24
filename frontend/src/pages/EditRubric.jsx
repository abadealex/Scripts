import React, { useState, useEffect } from 'react';
import RubricEditor from '../components/RubricEditor';

const EditRubric = () => {
  const [rubric, setRubric] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch existing rubric data from backend
    fetch('/api/v1/rubrics/current')
      .then(res => res.json())
      .then(data => {
        setRubric(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading rubric:', err);
        setLoading(false);
      });
  }, []);

  const handleSave = (updatedRubric) => {
    // Save updated rubric back to backend
    fetch('/api/v1/rubrics/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updatedRubric),
    })
      .then(res => {
        if (res.ok) alert('Rubric saved successfully!');
        else alert('Failed to save rubric.');
      })
      .catch(err => alert('Error saving rubric: ' + err.message));
  };

  return (
    <div className="edit-rubric-page container">
      <h1>Edit Rubric</h1>
      {loading && <p>Loading rubric...</p>}
      {!loading && rubric && <RubricEditor rubric={rubric} onSave={handleSave} />}
      {!loading && !rubric && <p>No rubric data found.</p>}
    </div>
  );
};

export default EditRubric;
