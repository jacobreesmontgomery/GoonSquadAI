from fastapi import APIRouter, Request

from typing import Any
from models.base import Empty, APIRequestPayload
from models.activities import DetailedActivities
from dao.strava_activities import StravaActivitiesDao
from utils.simple_logger import SimpleLogger

activities_dao = StravaActivitiesDao()
logger = SimpleLogger(log_level="INFO", class_name=__name__).logger

activities_router = APIRouter()


class ActivitiesAPI:
    """
    Handles all activities API requests.
    """

    @activities_router.get("/activities/basic-stats")
    async def get_activities(request: Request):
        """
        Retrieves all activities for the authenticated athlete.
        """
        # TODO: Implement this method
        logger.info("Getting activities")
        pass

    @activities_router.get(
        "/activities/detailed-stats",
        summary="Acquires a list of all activities from the database.",
        description="Acquires a a list of all activities from the strava_api.activities database table.",
        status_code=200,
        response_model=APIRequestPayload[DetailedActivities, Empty],
    )
    async def get_detailed_activities(
        request: Request,
    ) -> APIRequestPayload[DetailedActivities, Empty]:
        """
        Retrieves detailed statistics for all activities for the authenticated athlete.
        """
        logger.info("Getting detailed activities for the 'Database' page.")

        response = activities_dao.get_detailed_activities()

        return APIRequestPayload(
            data=DetailedActivities.model_validate(detailed_activities=response),
            meta=Empty(),
        )
