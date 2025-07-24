from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from smartscripts.ai.gpt_explainer import generate_explanation

router = APIRouter()

class FeedbackRequest(BaseModel):
    answer_id: str
    student_answer: str
    rubric_id: str

class FeedbackResponse(BaseModel):
    explanation: str

@router.post("/gpt_feedback", response_model=FeedbackResponse)
async def get_gpt_feedback(request: FeedbackRequest):
    try:
        explanation = generate_explanation(
            answer=request.student_answer,
            rubric_id=request.rubric_id
        )
        return FeedbackResponse(explanation=explanation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
