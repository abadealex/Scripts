✅ 1. FeedbackOverlay.jsx
Location: src/components/FeedbackOverlay.jsx
This component visually overlays feedback (tick, cross, etc.) on an image of the student's graded submission.

jsx
Copy
Edit
// src/components/FeedbackOverlay.jsx
import React from 'react';
import styles from '../styles/components/FeedbackOverlay.module.css';

const FeedbackOverlay = ({ imageUrl, feedbackItems = [] }) => {
  return (
    <div className={styles.overlayContainer}>
      <img src={imageUrl} alt="Graded Submission" className="img-fluid" />

      {feedbackItems.map((item, index) => {
        const { type, x, y, comment } = item;
        const style = {
          left: `${x}%`,
          top: `${y}%`,
        };

        if (type === 'highlight') {
          return (
            <div
              key={index}
              className={styles.highlightBox}
              style={{
                ...style,
                width: `${item.width}%`,
                height: `${item.height}%`,
              }}
            />
          );
        }

        if (type === 'comment') {
          return (
            <div key={index} className={styles.commentBubble} style={style}>
              💬 {comment}
            </div>
          );
        }

        const iconMap = {
          tick: 'tick.png',
          cross: 'cross.png',
          half: 'half_tick.png',
          override: 'icon_1.png',
        };

        return (
          <img
            key={index}
            src={`/static/overlays/${iconMap[type]}`}
            alt={type}
            className={`${styles.overlayIcon} ${styles[type]}`}
            style={style}
          />
        );
      })}
    </div>
  );
};

export default FeedbackOverlay;