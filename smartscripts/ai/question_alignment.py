# smartscripts/ai/question_alignment.py

from smartscripts.ai.text_matching import semantic_similarity


def align_questions(student_blocks, guide_questions, threshold=0.7):
    """
    Align OCR-extracted answer blocks with the marking guide questions using semantic similarity.

    Args:
        student_blocks (list[str]): Raw extracted text blocks from student's submission.
        guide_questions (list[dict]): Guide questions, each must have 'id' and 'question'.
        threshold (float): Minimum similarity to consider a match.

    Returns:
        dict: Mapping of guide_question_id -> matched student_answer_text
    """
    alignment = {}
    used_indices = set()

    for gq in guide_questions:
        best_score = 0
        best_index = -1
        best_text = ""

        for i, text in enumerate(student_blocks):
            if i in used_indices:
                continue

            score = semantic_similarity(gq["question"], text)
            if score > best_score:
                best_score = score
                best_index = i
                best_text = text

        if best_score >= threshold:
            alignment[str(gq["id"])] = best_text
            used_indices.add(best_index)
        else:
            alignment[str(gq["id"])] = ""  # No confident match

    return alignment


def batch_align_multiple_submissions(submissions, guide_questions, threshold=0.7):
    """
    Optional helper: Align multiple submissions at once.

    Args:
        submissions (list[list[str]]): List of OCR blocks for each student.
        guide_questions (list[dict]): Standard guide.
        threshold (float): Semantic threshold for matching.

    Returns:
        list[dict]: List of aligned answers (like align_questions output).
    """
    return [
        align_questions(blocks, guide_questions, threshold)
        for blocks in submissions
    ]
