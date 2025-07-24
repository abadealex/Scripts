// routes/reviews.js

const express = require('express');
const router = express.Router();

// Simulated in-memory data store for demo purposes
const reviewsData = {
  // Example entry:
  // 'sub123': {
  //   studentName: "John Doe",
  //   totalScore: 8.5,
  //   maxScore: 10,
  //   percentage: 85,
  //   questions: [ ... ],
  //   feedback: "Good overall",
  //   comments: ["Needs more detail on question 2"],
  //   overrides: { q2: 3 }  // override scores by question id
  // }
};

// GET review + feedback by submissionId
router.get('/:submissionId', (req, res) => {
  const submissionId = req.params.submissionId;
  const review = reviewsData[submissionId];

  if (!review) {
    return res.status(404).json({ error: 'Review not found for submissionId ' + submissionId });
  }

  res.json(review);
});

// POST update feedback, comments, overrides for a submission
router.post('/:submissionId/feedback', (req, res) => {
  const submissionId = req.params.submissionId;
  const { feedback, comments, overrides } = req.body;

  if (!reviewsData[submissionId]) {
    // If no existing review, create a new record with empty default fields
    reviewsData[submissionId] = {
      studentName: '',
      totalScore: 0,
      maxScore: 0,
      percentage: 0,
      questions: [],
      feedback: '',
      comments: [],
      overrides: {}
    };
  }

  // Update fields if provided
  if (typeof feedback === 'string') {
    reviewsData[submissionId].feedback = feedback;
  }
  if (Array.isArray(comments)) {
    // Append new comments (you could also replace)
    reviewsData[submissionId].comments = comments;
  }
  if (typeof overrides === 'object' && overrides !== null) {
    reviewsData[submissionId].overrides = overrides;
  }

  // Return updated review data
  res.json(reviewsData[submissionId]);
});

module.exports = router;
