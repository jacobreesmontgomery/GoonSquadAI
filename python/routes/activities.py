from fastapi import APIRouter, Request

from typing import Any
from models.base import Empty, APIRequestPayload, APIResponsePayload
from models.activities import DetailedActivities, UpdatedActivities
from dao.strava_activities import StravaActivitiesDao
from repositories.activities import ActivitiesRepository
from utils.simple_logger import SimpleLogger

activities_repository = ActivitiesRepository()
logger = SimpleLogger(class_name=__name__).logger

activities_router = APIRouter()


class ActivitiesAPI:
    """
    Handles all activities API requests.
    """

    # TODO: Complete this route
    @activities_router.get("/activities/basic-stats")
    async def get_activities(request: Request):
        """
        Retrieves all activities for the authenticated athlete.
        """

        response = activities_repository.get_basic_activities()
        pass

    # TODO: Complete this route
    @activities_router.get(
        "/activities/detailed-stats",
        summary="Acquires a list of all activities from the database.",
        description="Acquires a a list of all activities from the strava_api.activities database table.",
        status_code=200,
        response_model=APIResponsePayload[DetailedActivities, Empty],
    )
    async def get_detailed_activities(
        request: Request,
    ) -> APIResponsePayload[DetailedActivities, Empty]:
        """
        Retrieves detailed statistics for all activities for the authenticated athlete.
        """

        response = activities_repository.get_detailed_activities()
        return response

    # TODO: Complete this route
    @activities_router.get(
        "/activities/update-database-activities",
        summary="Updates the database with the latest activities.",
        description="Updates the database with the latest activities (new or updated) for each authenticated athlete.",
        status_code=200,
        response_model=APIResponsePayload[UpdatedActivities, Empty],
    )
    async def update_database_activities(
        request: Request,
    ) -> APIResponsePayload[UpdatedActivities, Empty]:
        """
        Updates the database with the latest activities for each authenticated athlete.
        """

        response = activities_repository.update_database_activities()
        return response
