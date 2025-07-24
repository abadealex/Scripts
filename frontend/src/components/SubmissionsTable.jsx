const handleDelete = async (submissionId) => {
  const confirmed = window.confirm('Are you sure you want to delete this submission?');
  if (!confirmed) return;

  try {
    await axios.delete(`/api/v1/submission/${submissionId}`);
    alert('Submission deleted.');
    // Refresh list
  } catch (err) {
    console.error(err);
    alert('Failed to delete submission.');
  }
};
