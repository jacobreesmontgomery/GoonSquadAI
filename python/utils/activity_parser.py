from datetime import datetime, time
from re import findall
from os import getenv
from stravalib.model import Activity

from services.database import DatabaseService
from services.strava import StravaAPI, StravaAuthorization
from dao.strava_activities import StravaActivitiesDao
from .formatter import Formatter
from .simple_logger import SimpleLogger

logger = SimpleLogger(class_name=__name__).logger

CLIENT_ID = getenv("CLIENT_ID")
CLIENT_SECRET = getenv("CLIENT_SECRET")
REDIRECT_URI = getenv("REDIRECT_URI")


class ActivityParser:

    def __init__(self):
        self.formatter = Formatter()
        self.database_service = DatabaseService()
        self.strava_activities_dao = StravaActivitiesDao(self.database_service)

    def parse_description(self, description):
        """
        The user can optionally include RPE, rating, average power, and a sleep rating in their activity description.
        If included, we'll parse these fields out and include them in the returned dictionary.

        Example description: "RPE:3|RATING:8|POWER:135|SLEEP:8. Good run! No issues."

        :param description: The activity description string.

        :return: A tuple containing RPE, rating, average power, and sleep rating values.
        """
        OPTIONAL_FIELDNAMES = ["RPE", "RATING", "POWER", "SLEEP"]
        fields = {key: 0 for key in OPTIONAL_FIELDNAMES}
        logger.debug(f"fields: {fields}")
        pattern = r"(\w+):\s*(\d+)"
        matches = findall(pattern, description)

        for key, value in matches:
            key = str(key).strip().upper()
            if key in OPTIONAL_FIELDNAMES:
                fields[key] = str(value).strip(". ")
                fields[key] = int(fields[key])  # Converting to int

        rpe = fields["RPE"]
        rating = fields["RATING"]
        avg_power = fields["POWER"]
        sleep_rating = fields["SLEEP"]

        logger.debug(
            f"END of parse_description() w/ return(s)... \n\trpe: {rpe}, rating: {rating}, avg_power: {avg_power}, sleep_rating: {sleep_rating}\n"
        )
        return rpe, rating, avg_power, sleep_rating

    def parse_start_date(self, start_date: datetime):
        """
        Parses the start date from a datetime object and returns it in various formats.

        :param start_date: The datetime object to parse.

        :return: A tuple containing time, week_day, month, day, and year.
        """
        week_day = start_date.strftime("%a").upper()
        month = int(start_date.strftime("%m"))
        day = int(start_date.strftime("%d"))
        year = int(start_date.strftime("%Y"))
        run_time = time(
            hour=start_date.hour,
            minute=start_date.minute,
            second=start_date.second,
            tzinfo=start_date.tzinfo,
        )

        logger.debug(
            f"\nEND of parse_start_date() w/ return(s)...\n\ttime: {time}, week_day: {week_day}, month: {month}, day: {day}, year: {year}\n"
        )
        return run_time, week_day, month, day, year

    def convert_activities_to_list_of_dicts_postgres(
        self, activities: list[Activity]
    ) -> list[dict]:
        """
        Converts the detailed activities to a list of dicts,
        digestable by SQLAlchemy for the PostgreSQL database injections.

        :param activities: List of Activity objects.

        :return: List of dictionaries containing formatted activity data.
        """
        logger.debug(
            f"\nSTART of convert_activities_to_list_of_dicts_postgres() w/ arg(s)...\n\tactivities: {activities}"
        )
        activities_list = list()
        for activity in activities:
            # Initial calculations
            rpe, run_rating, avg_power, sleep_rating = self.parse_description(
                activity.description if activity.description else ""
            )
            run_time, week_day, month, day, year = self.parse_start_date(
                activity.start_date_local
            )
            str_formatted_time, time_obj = self.formatter.format_seconds(
                activity.moving_time
            )
            str_formatted_moving_time, moving_time_obj = self.formatter.calculate_pace(
                float(activity.moving_time.total_seconds()),
                float(activity.distance * 0.000621371),
            )

            # Establishing the activity dict
            activity_dict = {
                "activity_id": activity.id,
                "athlete_id": activity.athlete.id,
                "name": activity.name,
                "moving_time": time_obj,
                "moving_time_s": activity.moving_time.total_seconds(),
                "distance_mi": round(
                    float(activity.distance) / 1609.34, 2
                ),  # Converting meters to miles
                "pace_min_mi": moving_time_obj,
                "avg_speed_ft_s": round(
                    float(str(activity.average_speed).split()[0]) * 3.28084, 2
                ),
                "full_datetime": activity.start_date,
                "time": run_time,
                "week_day": week_day,
                "month": month,
                "day": day,
                "year": year,
                "spm_avg": (
                    round(activity.average_cadence * 2, 2)
                    if activity.average_cadence
                    else 0.0
                ),
                "hr_avg": (
                    round(activity.average_heartrate, 2)
                    if activity.average_heartrate
                    else 0.0
                ),
                "wkt_type": activity.workout_type,
                "description": activity.description,
                "total_elev_gain_ft": round(
                    float(str(activity.total_elevation_gain).split()[0]) * 3.28084, 2
                ),
                "manual": activity.manual,
                "max_speed_ft_s": round(
                    float(str(activity.max_speed).split()[0]) * 3.28084, 2
                ),
                "calories": round(activity.calories, 0),
                "achievement_count": activity.achievement_count,
                "kudos_count": activity.kudos_count,
                "comment_count": activity.comment_count,
                "athlete_count": activity.athlete_count,
                "rpe": rpe,
                "rating": run_rating,
                "avg_power": avg_power,
                "sleep_rating": sleep_rating,
            }  # add more fields as needed
            activities_list.append(activity_dict)
        logger.debug(
            f"\nEND of convert_activities_to_list_of_dicts_postgres() w/ return(s)...\n\tactivities_list: {activities_list}\n"
        )
        return activities_list

    def get_longest_run_no_existing_data(self, new_athlete_runs):
        """
        Takes in the athlete's new data and determines the longest run
        of that data.

        NOTE: This is used in the context of their not being existing data
        for the given athlete in the recap file.

        :param new_athlete_runs: List of dictionaries containing the athlete's new run data.

        :return: A tuple containing the longest run distance and its date.
        """
        logger.debug(
            f"\nSTART of get_longest_run_no_existing_data()\n\tnew_athlete_runs: {new_athlete_runs}"
        )
        longest_run = float(new_athlete_runs[0]["DISTANCE (MI)"])
        longest_run_date = new_athlete_runs[0]["FULL DATE"]
        for new_run in new_athlete_runs[1:]:
            try:
                new_run_distance = float(new_run["DISTANCE (MI)"])
            except ValueError as e:
                logger.error(
                    f"Error: {e}"
                )  # Output: Error: could not convert string to float: 'abc'

            if new_run_distance > longest_run:
                longest_run = new_run_distance
                longest_run_date = new_run["FULL DATE"]
        logger.debug(
            f"END of get_longest_run_no_existing_data()\n\tlongest_run: {longest_run}\n\tlongest_run_date: {longest_run_date}\n"
        )
        return longest_run, longest_run_date

    def get_longest_run(self, new_athlete_runs, existing_recap_data):
        """
        Takes in the athlete's new data and determines the longest run
        of that data WITH the existing recap data.

        NOTE: This is used in the context of their being existing data
        for the given athlete in the recap file.

        :param new_athlete_runs: List of dictionaries containing the athlete's new run data.
        :param existing_recap_data: Dictionary containing the athlete's existing recap data.

        :return: A tuple containing the longest run distance and its date.
        """
        logger.debug(
            f"\nSTART of get_longest_run()\n\tnew_athlete_runs: {new_athlete_runs}\n\texisting_recap_data: {existing_recap_data}"
        )
        longest_run = float(existing_recap_data["LONGEST RUN"])
        longest_run_date = existing_recap_data["LONGEST RUN DATE"]
        logger.debug(
            f"longest_run: {longest_run}\nlongest_run_date: {longest_run_date}"
        )
        for new_run in new_athlete_runs[1:]:
            try:
                new_run_distance = float(new_run["DISTANCE (MI)"])
            except ValueError as e:
                logger.error(
                    f"Error: {e}"
                )  # Output: Error: could not convert string to float: 'abc'

            if new_run_distance > longest_run:
                longest_run = new_run_distance
                longest_run_date = new_run["FULL DATE"]
        logger.debug(
            f"END of get_longest_run()\n\tlongest_run: {longest_run}\n\tlongest_run_date: {longest_run_date}\n"
        )
        return longest_run, longest_run_date

    def get_and_insert_athlete_activities_into_db(
        self,
        athlete_id: int,
        refresh_token: str,
        start_date: str = None,
        end_date: str = None,
    ):
        """
        Retrieve all activities for a specific athlete from Strava API,
        format them, and insert into a PostgreSQL database.

        :param athlete_id: The athlete's ID.
        :param refresh_token: The athlete's refresh token.
        :param start_date: Limit results to activities after this timestamp.
        :param end_date: Limit results to activities before this timestamp.

        :return: None
        """
        logger.debug("\nSTART of get_and_insert_athlete_activities_into_db()...\n")

        # Get auth client and access token
        authorization_client = StravaAuthorization(
            client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI
        )
        access_token = authorization_client.exchange_refresh_token(
            refresh_token=refresh_token
        )
        strava_client = StravaAPI(access_token=access_token)

        # Retrieve (and format) the athlete's activities between the after and before timeframe
        activities = strava_client.get_activities(
            athlete_id=athlete_id, start_date=start_date, end_date=end_date
        )
        if not activities:
            logger.debug(f"No activities were found for athlete {athlete_id}.")
            return  # No activities to insert
        detailed_activities = self.convert_activities_to_list_of_dicts_postgres(
            activities=activities
        )

        logger.debug("\nSTART of get_and_insert_athlete_activities_into_db()...\n")

        # Get auth client and access token
        authorization_client = StravaAuthorization(
            client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI
        )
        access_token = authorization_client.exchange_refresh_token(
            refresh_token=refresh_token
        )
        strava_client = StravaAPI(access_token=access_token)

        # Retrieve (and format) the athlete's activities between the after and before timeframe
        activities = strava_client.get_activities(
            athlete_id=athlete_id, start_date=start_date, end_date=end_date
        )
        if not activities:
            logger.debug(f"No activities were found for athlete {athlete_id}.")
            return  # No activities to insert
        detailed_activities = self.convert_activities_to_list_of_dicts_postgres(
            activities=activities
        )

        # Insert the formatted activities into the PostgreSQL database
        for activity in detailed_activities:
            self.strava_activities_dao.upsert_activity(activity_data=activity)
        logger.info(
            f"Upserted {len(detailed_activities)} activities into strava_api.activities."
        )

        logger.debug("END of get_and_insert_athlete_activities_into_db()...\n")
