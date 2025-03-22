from typing import Any
from models.base import Empty, APIResponsePayload
from models.activities import DetailedActivities, UpdatedActivities
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

    def get_basic_activities(self) -> Any:
        """
        Retrieves all activities for the authenticated athlete.
        """

        logger.info("Getting activities")

        pass

    def get_detailed_activities(self) -> APIResponsePayload[DetailedActivities, Empty]:
        """
        Retrieves detailed statistics for all activities for the authenticated athlete.
        """

        detailed_activities = self.strava_activities_dao.get_detailed_activities()

        return APIResponsePayload(
            data=DetailedActivities.model_validate(
                detailed_activities=detailed_activities
            ),
            meta=Empty(),
        )

    def update_database_activities(
        self,
    ) -> APIResponsePayload[UpdatedActivities, Empty]:
        """
        Updates the database with the latest activities.
        """

        logger.info("Updating the database with the latest activities.")

        all_users = self.strava_athlete_dao.get_all_authenticated_athletes()
        for user in all_users:
            num_upserts = (
                self.activity_parser.get_and_insert_athlete_activities_into_db(
                    athlete_id=user.athlete_id, refresh_token=user.refresh_token
                )
            )

        return APIResponsePayload(
            data=UpdatedActivities(num_updated_activities=num_upserts), meta=Empty()
        )
