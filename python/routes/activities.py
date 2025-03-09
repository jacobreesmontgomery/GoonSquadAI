from fastapi import APIRouter, Request

from dao.strava_activities import StravaActivitiesDao
from utils.simple_logger import SimpleLogger

logger = SimpleLogger(log_level="INFO", class_name=__name__).logger

activities_router = APIRouter()


class ActivitiesAPI:
    """
    Handles all activities API requests.
    """

    @activities_router.get("/activities/basic-stats")
    async def get_activities(self, request: Request):
        """
        Retrieves all activities for the authenticated athlete.
        """
        # TODO: Implement this method
        logger.info("Getting activities")
        pass

    @activities_router.get("/activities/detailed-stats")
    async def get_detailed_activities(self, request: Request):
        """
        Retrieves detailed statistics for all activities for the authenticated athlete.
        """
        # TODO: Implement this method
        logger.info("Getting detailed activities")
        pass
