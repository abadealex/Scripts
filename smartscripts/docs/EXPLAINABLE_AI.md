# Explainable AI (XAI) in SmartScripts

SmartScripts uses Explainable AI to help both students and teachers understand *why* a particular answer was marked as incorrect, and how it can be improved.

---

## 💡 How Explanation Generation Works

1. **Reasoning Trace (`reasoning_trace.py`)**  
   - Captures the logical steps taken to mark an answer.
   - Includes rubric rule triggers, partial credit logic, and key phrase mismatches.
   - Output: A structured trace (JSON) showing which rule failed and why.

2. **LLM Explanation (`gpt_explainer.py`)**  
   - The trace is sent to GPT-4 to generate a natural-language explanation.
   - Prompt includes:
     - Student’s answer
     - Rubric criteria
     - Reasoning trace
     - Optional correct example

3. **Frontend Display**  
   - Displayed in `ExplanationModal.js` and `AnswerFeedback.js` components.
   - Teachers can view the full trace; students see a simplified version.

---

## 🔎 Modes of Explainability

| Mode    | Audience | Content                                |
|---------|----------|-----------------------------------------|
| Teacher | Full trace + GPT summary                          |
| Student | GPT-generated explanation + targeted hints        |
| Admin   | Raw trace + audit logs                            |

---

## 🛠️ Prompt Structure

```json
{
  "rubric_rule": "Claim must be supported by at least one direct quote from the text.",
  "student_answer": "The character was upset because things weren’t going their way.",
  "reasoning_trace": {
    "match_found": false,
    "missing_elements": ["direct quote"],
    "confidence": 0.7
  }
}
