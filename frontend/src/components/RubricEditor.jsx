// 
import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function RubricEditor({ rubricId, onSave }) {
  const [criteria, setCriteria] = useState([]);
  const [title, setTitle] = useState('');

  useEffect(() => {
    if (rubricId) {
      axios.get(`/api/v1/rubrics/${rubricId}`).then(res => {
        setTitle(res.data.title);
        setCriteria(res.data.criteria);
      });
    }
  }, [rubricId]);

  const addCriterion = () => {
    setCriteria([...criteria, { name: '', points: 1 }]);
  };

  const updateCriterion = (idx, field, value) => {
    const newCrit = [...criteria];
    newCrit[idx][field] = field === 'points' ? parseInt(value, 10) : value;
    setCriteria(newCrit);
  };

  const submit = () => {
    const payload = { title, criteria };
    const req = rubricId
      ? axios.put(`/api/v1/rubrics/${rubricId}`, payload)
      : axios.post('/api/v1/rubrics', payload);

    req.then(res => onSave(res.data));
  };

  return (
    <div className="rubric-editor">
      <h2>{rubricId ? 'Edit' : 'New'} Rubric</h2>
      <input
        type="text"
        placeholder="Rubric Title"
        value={title}
        onChange={e => setTitle(e.target.value)}
      />
      <ul>
        {criteria.map((c, i) => (
          <li key={i}>
            <input
              type="text"
              placeholder="Criterion name"
              value={c.name}
              onChange={e => updateCriterion(i, 'name', e.target.value)}
            />
            <input
              type="number"
              min="0"
              value={c.points}
              onChange={e => updateCriterion(i, 'points', e.target.value)}
            />
          </li>
        ))}
      </ul>
      <button onClick={addCriterion}>Add Criterion</button>
      <button onClick={submit}>Save Rubric</button>
    </div>
  );
}

// ExplanationModal.js
import React from 'react';

export default function ExplanationModal({ show, onClose, explanation }) {
  if (!show) return null;

  return (
    <div className="modal-backdrop">
      <div className="modal-content">
        <h3>Why This Was Marked Incorrectly</h3>
        <p>{explanation}</p>
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  );
}

// BiasAuditDashboard.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';

export default function BiasAuditDashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    axios.get('/api/v1/audit/latest').then(res => setData(res.data));
  }, []);

  if (!data) return <p>Loading audit data…</p>;

  const chartData = {
    labels: Object.keys(data.bias_heatmap.question_type),
    datasets: [
      {
        label: 'Override Frequency by Question Type',
        backgroundColor: 'rgba(75,192,192,0.4)',
        data: Object.values(data.bias_heatmap.question_type),
      },
    ],
  };

  return (
    <div className="bias-dashboard">
      <h2>AI Fairness Audit Overview</h2>
      <p><strong>Overall Override Rate:</strong> {data.override_rate.toFixed(1)}%</p>
      <Bar data={chartData} />
    </div>
  );
}

// SocraticPromptBox.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function SocraticPromptBox({ questionId, studentAnswer }) {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (questionId && studentAnswer) {
      setLoading(true);
      axios
        .post('/api/v1/gpt_feedback', {
          type: 'socratic',
          questionId,
          answer: studentAnswer,
        })
        .then(res => setPrompt(res.data.prompt))
        .finally(() => setLoading(false));
    }
  }, [questionId, studentAnswer]);

  if (loading) return <p>Generating hint…</p>;
  if (!prompt) return null;

  return (
    <div className="socratic-prompt-box">
      <em>Try thinking about this:</em>
      <p>{prompt}</p>
    </div>
  );
}
