from fastapi import APIRouter, Request

from typing import Any
from models.base import Empty, APIRequestPayload, APIResponsePayload
from models.activities import (
    DetailedActivities,
    AllUpdatedActivities,
    UpdateDatabaseActivitiesRequest,
)
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
        description="Acquires a a list of all activities from the strava.activities database table.",
        status_code=200,
        response_model=APIResponsePayload[DetailedActivities, Empty],
    )
    async def get_detailed_activities(
        request: Request,
    ) -> APIResponsePayload[DetailedActivities, Empty]:
        """
        Retrieves detailed statistics for all activities for the authenticated athlete.
        """

        response = await activities_repository.get_detailed_activities()

        return response

    # TODO - JACOB: Run through the manual data injection process again so we get suffer score and perceived exertion...
    # Currently back to the start of 2024.
    @activities_router.post(
        "/activities/update-database-activities",
        summary="Updates the database with the latest activities.",
        description="Updates the database with the latest activities (new or updated) for each authenticated athlete.",
        status_code=200,
        response_model=APIResponsePayload[AllUpdatedActivities, Empty],
    )
    async def update_database_activities(
        payload: APIRequestPayload[UpdateDatabaseActivitiesRequest, Empty],
    ) -> APIResponsePayload[AllUpdatedActivities, Empty]:
        """
        Updates the database with the latest activities for each authenticated athlete.
        """

        response = await activities_repository.update_database_activities(
            start_date=payload.data.start_date,
            end_date=payload.data.end_date,
            limit=payload.data.limit,
            athlete_ids=payload.data.athlete_ids,
            bypass_db_check=payload.data.bypass_db_check,
        )

        return response
