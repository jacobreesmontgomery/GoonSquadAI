from stravalib.client import Client
from stravalib.exc import RateLimitExceeded
from stravalib.model import Activity, Athlete
from dao.strava_activities import StravaActivitiesDao
from datetime import datetime, timedelta
from stravalib.client import Client
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
    RetryError,
)
from os import getenv
from asyncio import to_thread, gather, Semaphore

from utils.simple_logger import SimpleLogger

logger = SimpleLogger(class_name=__name__).logger


class StravaAuthorization:
    """
    Responsible for authorization of a given athlete and acquiring their newest access token.
    """

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None):
        self.client_id = client_id if client_id else getenv("CLIENT_ID")
        self.client_secret = client_secret if client_secret else getenv("CLIENT_SECRET")
        self.redirect_uri = redirect_uri if redirect_uri else getenv("REDIRECT_URI")
        self.client = Client()

    async def get_authorization_url(self) -> str:
        """
        Generates the authorization URL for the athlete.

        :return: The authorization URL as a string.
        """
        return self.client.authorization_url(
            client_id=self.client_id, redirect_uri=self.redirect_uri
        )

    async def exchange_refresh_token(self, refresh_token: str) -> str:
        """
        Exchanges a refresh token for a new access token.

        :param refresh_token: The refresh token to exchange.
        :return: The new access token as a string.
        """
        token_response = self.client.refresh_access_token(
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=refresh_token,
        )
        return token_response["access_token"]

    async def exchange_authorization_code(self, code):
        """
        Exchanges an authorization code for an access token.

        :param code: The authorization code to exchange.
        :return: The token response.
        """
        token_response = self.client.exchange_code_for_token(
            client_id=self.client_id, client_secret=self.client_secret, code=code
        )
        return token_response


class ActivityRetrievalException(Exception):
    """
    Exception for detailed activity retrieval failures.
    """

    pass


class StravaAPI:
    """
    Responsible for making calls to the Strava API for activity data.
    """

    def __init__(self, access_token):
        self.access_token = access_token
        self.client = Client(access_token)
        self.strava_activities_dao = StravaActivitiesDao()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(min=1, max=10),
        retry=retry_if_exception_type(ActivityRetrievalException),
    )
    async def fetch_activities(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
    ) -> list[Activity] | None:
        """
        Retrieves all activities for the authenticated athlete.

        :param start_date: The start date, as an epoch timestamp, of the timeframe for activities (optional)
        :param end_date: The end date, as an epoch timestamp, of the timeframe for activities (optional)
        :param limit: The maximum number of activities to retrieve (optional)
        :return: A list of activities for the authenticated athlete.
        """
        try:
            logger.debug("Fetching activities...")
            result = await to_thread(
                self.client.get_activities,
                after=start_date,
                before=end_date,
                limit=limit,
            )
            logger.debug(f"Retrieved activities.")
            return result
        except RateLimitExceeded as e:
            logger.error(f"Strava API rate limit exceeded: {e}")
            return None
        except RetryError as e:
            logger.error(
                f"Failed to retrieve activities on final retry attempt [{e.last_attempt.attempt_number}]: {e}"
            )
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve activities: {e}")
            raise ActivityRetrievalException

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(min=1, max=10),
        retry=retry_if_exception_type(ActivityRetrievalException),
    )
    async def fetch_detailed_activity(self, activity_id: int) -> Activity | None:
        """
        Retrieves the detailed activity with the given ID.

        :param activity_id: The ID of the activity
        :return: A detailed activity.
        """
        try:
            logger.debug(f"Fetching detailed activity with ID {activity_id}...")
            result = await to_thread(self.client.get_activity, activity_id=activity_id)
            logger.debug(f"Detailed activity with ID {activity_id} retrieved.")
            return result
        except RateLimitExceeded as e:
            # TODO: Figure out why we're not hitting rate limit error here... UGH.
            logger.error(
                f"Strava API rate limit exceeded for activity [{activity_id}]: {e}"
            )
            return None
        except RetryError as e:
            logger.error(
                f"Failed to retrieve detailed activity [{activity_id}] on final retry attempt [{e.last_attempt.attempt_number}]: {e}"
            )
            return None
        except Exception as e:
            logger.error(
                f"Failed to retrieve detailed activity with ID [{activity_id}]: {e}"
            )
            raise ActivityRetrievalException(
                f"Failed to retrieve detailed activity with ID [{activity_id}]: {e}"
            )

    async def get_detailed_activities(
        self,
        activities: list[Activity],
        activity_types: list[str] = ["Run"],
        fields_to_check: dict[str, str] = {
            "name": "name",
            "description": "description",
            "workout_type": "wkt_type",
        },
        bypass_db_check: bool = False,
        max_concurrent_requests: int = 10,
    ) -> list[Activity]:
        """
        Gets the detailed activities of runs that are new or updated for specific fields.
        Uses concurrent API calls with a limit to prevent rate limiting issues.

        :param activities: list of Activity objects
        :param activity_types: list of activity types to include
        :param fields_to_check: dictionary mapping API field names to DB field names
        :param bypass_db_check: whether to bypass DB checks for existing activities
        :param max_concurrent_requests: maximum number of concurrent API requests
        :return: a list of detailed Activity objects
        """

        # Filter the activities to only include those of the specified types
        activities = [
            activity for activity in activities if activity.type in activity_types
        ]
        logger.info(
            f"Filtered down to {len(activities)} out of {len(activities)} total activities."
        )

        # List to store activities needing detailed info
        activities_to_fetch: list[Activity] = []

        # First pass: check database to determine which activities need updates
        if not bypass_db_check:
            for activity in activities:
                db_activity = await self.strava_activities_dao.get_activity(
                    activity_id=activity.id
                )

                # If present, compare the incoming activity against the corresponding DB entry
                if db_activity:
                    fields_that_differ = []
                    for api_field, db_field in fields_to_check.items():
                        if getattr(activity, api_field) != getattr(
                            db_activity, db_field
                        ):
                            fields_that_differ.append(api_field)

                    if not fields_that_differ:
                        logger.debug(
                            f"Activity [{activity.id}] has not been updated in the database for fields {list(fields_to_check.keys())}. Skipping the update."
                        )
                        continue  # Skip the update if no fields have changed
                    else:
                        logger.debug(
                            f"Activity [{activity.id}] has been updated in the database for fields {fields_that_differ}. Updating the activity in the database."
                        )

                activities_to_fetch.append(activity)
        else:
            # If bypassing DB check, fetch all activities
            activities_to_fetch = activities

        logger.info(
            f"Fetching detailed data for {len(activities_to_fetch)} activities with concurrency limit of {max_concurrent_requests}"
        )

        # Create a semaphore to limit concurrent requests
        semaphore = Semaphore(max_concurrent_requests)

        # Helper function to fetch a single activity with the semaphore
        async def fetch_with_semaphore(activity_id):
            async with semaphore:
                return await self.fetch_detailed_activity(activity_id=activity_id)

        # Create tasks for all activities to fetch
        fetch_tasks = [
            fetch_with_semaphore(activity.id) for activity in activities_to_fetch
        ]

        # Execute all tasks concurrently and wait for results
        detailed_results = await gather(*fetch_tasks, return_exceptions=True)

        # Process results, filtering out exceptions and None values
        detailed_activities: list[Activity] = []
        for i, result in enumerate(detailed_results):
            if isinstance(result, Exception):
                logger.error(
                    f"Error fetching activity [{activities_to_fetch[i].id}]: {result}"
                )
            elif result is None:
                logger.error(
                    f"No detailed activity was acquired for activity [{activities_to_fetch[i].id}]."
                )
            else:
                detailed_activities.append(result)

        logger.info(
            f"Successfully retrieved {len(detailed_activities)} detailed activities out of {len(activities_to_fetch)} requested."
        )
        return detailed_activities

    async def get_activities_this_week(
        self, bypass_db_check: bool = False
    ) -> list[Activity]:
        """
        Gets the athlete's activities for the current week.

        :param bypass_db_check: Whether to bypass the database check for existing activities (optional)
        :return: A list of the current week's activities
        """
        # Calculate the start and end of the current week in UTC
        today = datetime.now()
        start_of_week = (today - timedelta(days=today.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_of_week = (start_of_week + timedelta(days=6)).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        # Retrieve activities within the current week
        activities = await self.fetch_activities(
            start_date=start_of_week, end_date=end_of_week
        )
        if not activities:
            logger.debug("No activities acquired for this week.")
            return []  # No activities acquired, return an empty list

        # Get the detailed activities from the basic list above
        detailed_activities = await self.get_detailed_activities(
            activities=activities, bypass_db_check=bypass_db_check
        )
        return detailed_activities

    async def get_activities(
        self,
        athlete_id: int,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        bypass_db_check: bool = False,
    ) -> list[Activity]:
        """
        Gets the athlete's activities for a default, or specified, timeframe.

        :param athlete_id: The athlete's ID
        :param start_date: The start date, as an epoch timestamp, of the timeframe for activities (optional)
        :param end_date: The end date, as an epoch timestamp, of the timeframe for activities (optional)
        :param limit: The maximum number of activities to retrieve (optional)
        :param bypass_db_check: Whether to bypass the database check for existing activities (optional)
        :return: A list of activities for the specified athlete and timeframe.
        """
        try:
            activities = await self.fetch_activities(
                start_date=start_date, end_date=end_date, limit=limit
            )
            if not activities:
                logger.debug(
                    f"No activities acquired for athlete ID {athlete_id} in the specified timeframe."
                )
                return []  # No activities acquired, return an empty list

            detailed_activities = await self.get_detailed_activities(
                activities=activities, bypass_db_check=bypass_db_check
            )
            return detailed_activities
        except Exception as e:
            logger.error(
                f"Failed to retrieve activities for athlete ID {athlete_id}: {e}"
            )
            return None

    async def get_athlete_data(self) -> Athlete:
        """
        Gets the athlete's basic information via the /athlete endpoint.

        :return: An Athlete object for the given athlete.
        """
        try:
            athlete_data = self.client.get_athlete()
            return athlete_data
        except Exception as e:
            logger.error(f"An error occurred while retrieving athlete data: {e}")
            return None
