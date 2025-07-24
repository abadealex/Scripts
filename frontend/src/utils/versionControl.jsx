// versionControl.js
// Helper functions for versioning: hashing, rollback, etc.

import crypto from 'crypto';

// Generate a SHA-256 hash from a string (e.g., rubric JSON)
export function generateHash(content) {
  return crypto.createHash('sha256').update(content).digest('hex');
}

// Compare two versions by their hashes
export function isSameVersion(hash1, hash2) {
  return hash1 === hash2;
}

// Rollback logic placeholder (would interface with backend/version store)
export async function rollbackVersion(versionId) {
  // Example: call API to rollback
  const response = await fetch(`/api/v1/version_control/rollback/${versionId}`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Rollback failed');
  return response.json();
}
