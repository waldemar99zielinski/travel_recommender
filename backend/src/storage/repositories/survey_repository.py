from __future__ import annotations

from uuid import UUID

from sqlmodel import Session
from sqlmodel import col
from sqlmodel import select

from storage.models.survey_question import SurveyQuestion
from storage.models.survey_result import SurveyResult


class SurveyRepository:
    """Repository for survey questions and results."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_questions(self) -> list[SurveyQuestion]:
        statement = select(SurveyQuestion).order_by(col(SurveyQuestion.id))
        return list(self.session.exec(statement).all())

    def save_result(self, result: SurveyResult) -> SurveyResult:
        self.session.add(result)
        self.session.flush()
        self.session.refresh(result)
        return result

    def list_results(self) -> list[SurveyResult]:
        statement = select(SurveyResult).order_by(col(SurveyResult.id))
        return list(self.session.exec(statement).all())

    def list_results_by_user(self, user_id: UUID) -> list[SurveyResult]:
        statement = (
            select(SurveyResult)
            .where(col(SurveyResult.user_id) == user_id)
            .order_by(col(SurveyResult.id))
        )
        return list(self.session.exec(statement).all())

    def list_results_by_session(self, session_id: UUID) -> list[SurveyResult]:
        statement = (
            select(SurveyResult)
            .where(col(SurveyResult.session_id) == session_id)
            .order_by(col(SurveyResult.id))
        )
        return list(self.session.exec(statement).all())
