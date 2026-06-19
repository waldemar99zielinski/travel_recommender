from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import status

from api.schemas.survey import SurveyQuestionDto
from api.schemas.survey import SurveyResultCreateRequestDto
from api.schemas.survey import SurveyResultResponseDto
from storage.models.survey_result import SurveyResult
from storage.models.survey_result import SurveyResultsData
from storage.stores.survey_store import SurveyStore
from utils.logger import LoggerManager

router = APIRouter(prefix="/api/v1/survey")
logger = LoggerManager.get_logger(__name__)


def _get_survey_store(request: Request) -> SurveyStore:
    return request.app.state.storage.survey


@router.get("/questions", response_model=list[SurveyQuestionDto])
def list_questions(
    store: SurveyStore = Depends(_get_survey_store),
) -> list[SurveyQuestionDto]:
    questions = store.list_questions()
    return [SurveyQuestionDto(id=q.id, question_text=q.question_text) for q in questions]


@router.post("/results", response_model=SurveyResultResponseDto, status_code=status.HTTP_201_CREATED)
def save_result(
    payload: SurveyResultCreateRequestDto,
    store: SurveyStore = Depends(_get_survey_store),
) -> SurveyResultResponseDto:
    result = SurveyResult(
        user_id=payload.user_id,
        session_id=payload.session_id,
        results=SurveyResultsData(scores=payload.scores),
        comment=payload.comment,
    )
    saved = store.save_result(result)
    return SurveyResultResponseDto(
        id=saved.id,
        user_id=saved.user_id,
        session_id=saved.session_id,
        scores=saved.results.scores,
        comment=saved.comment,
    )
