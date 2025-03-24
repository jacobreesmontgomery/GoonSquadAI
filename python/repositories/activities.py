from typing import Any
from asyncio import gather, Semaphore

from models.base import Empty, APIResponsePayload
from models.athlete import Athlete
from models.activities import (
    DetailedActivities,
    AllUpdatedActivities,
    UpdatedAthleteActivities,
)
from dao.strava_activities import StravaActivitiesDao
from dao.strava_athlete import StravaAthleteDao
from utils.simple_logger import SimpleLogger
from utils.activity_parser import ActivityParser

activities_dao = StravaActivitiesDao()
logger = SimpleLogger(class_name=__name__).logger


class ActivitiesRepository:
    """
    Repository to manage the data layer for activities.
    """

    def __init__(self):
        self.strava_activities_dao = StravaActivitiesDao()
        self.strava_athlete_dao = StravaAthleteDao()
        self.activity_parser = ActivityParser()
        self.db_semaphore = Semaphore(10)  # Limit to 10 concurrent connections

    def get_basic_activities(self) -> Any:
        """
        Retrieves all activities for the authenticated athlete.
        """

        logger.info("Getting activities")

        pass

    async def get_detailed_activities(
        self,
    ) -> APIResponsePayload[DetailedActivities, Empty]:
        """
        Retrieves detailed statistics for all activities for the authenticated athlete.
        """

        detailed_activities = await self.strava_activities_dao.get_detailed_activities()

        return APIResponsePayload(
            data=DetailedActivities.model_validate(
                detailed_activities=detailed_activities
            ),
            meta=Empty(),
        )

    async def update_database_activities(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
    ) -> APIResponsePayload[AllUpdatedActivities, Empty]:
        """
        Updates the database with the latest activities asynchronously for each athlete.
        """

        logger.info("Updating the database with the latest activities asynchronously.")

        all_users = await self.strava_athlete_dao.get_all_authenticated_athletes()

        async def process_user(user: Athlete) -> UpdatedAthleteActivities:
            """Process a single user's activities asynchronously"""
            try:
                async with self.db_semaphore:
                    logger.info(f"Processing user {user.athlete_id}")
                    num_upserts = await self.activity_parser.get_and_insert_athlete_activities_into_db(
                        athlete_id=user.athlete_id,
                        refresh_token=user.refresh_token,
                        start_date=start_date,
                        end_date=end_date,
                        limit=limit,
                    )
                return UpdatedAthleteActivities(
                    athlete_id=user.athlete_id, num_updated_activities=num_upserts
                )
            except Exception as e:
                logger.error(f"Error processing user {user.athlete_id}: {str(e)}")
                return UpdatedAthleteActivities(
                    athlete_id=user.athlete_id, num_updated_activities=0
                )

        # Create and gather all tasks
        tasks = [process_user(user) for user in all_users]
        updated_athlete_activities = await gather(*tasks)

        return APIResponsePayload(
            data=AllUpdatedActivities(updated_activities=updated_athlete_activities),
            meta=Empty(),
        )
