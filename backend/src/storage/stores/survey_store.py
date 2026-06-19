from __future__ import annotations

from uuid import UUID

from storage.db.unit_of_work import StorageUnitOfWork
from storage.models.survey_question import SurveyQuestion
from storage.models.survey_result import SurveyResult
from storage.repositories.survey_repository import SurveyRepository


class SurveyStore:
    """Store facade for survey questions and results."""

    def __init__(self, unit_of_work: StorageUnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    def list_questions(self) -> list[SurveyQuestion]:
        with self.unit_of_work.read() as session:
            repository = SurveyRepository(session)
            return repository.list_questions()

    def save_result(self, result: SurveyResult) -> SurveyResult:
        with self.unit_of_work.write() as session:
            repository = SurveyRepository(session)
            return repository.save_result(result)

    def list_results(self) -> list[SurveyResult]:
        with self.unit_of_work.read() as session:
            repository = SurveyRepository(session)
            return repository.list_results()

    def list_results_by_user(self, user_id: UUID) -> list[SurveyResult]:
        with self.unit_of_work.read() as session:
            repository = SurveyRepository(session)
            return repository.list_results_by_user(user_id)

    def list_results_by_session(self, session_id: UUID) -> list[SurveyResult]:
        with self.unit_of_work.read() as session:
            repository = SurveyRepository(session)
            return repository.list_results_by_session(session_id)
