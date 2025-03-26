from sqlalchemy.dialects.postgresql import insert

from models.athlete import Activity
from services.database import DatabaseService
from utils.simple_logger import SimpleLogger

logger = SimpleLogger(class_name=__name__).logger


class StravaActivitiesDao:
    """
    Responsible for managing Strava activity data in the database.
    """

    def __init__(self, db_service: DatabaseService = DatabaseService()):
        """
        Initialize the StravaActivitiesDao with a database service.

        :param db_service: An instance of DatabaseService for session management.
        """
        self.db_service = db_service

    async def upsert_activity(self, activity_data: dict) -> int:
        """
        Upserts an activity record into the database. If the activity exists,
        it updates the record; otherwise, it inserts a new record.

        :param activity_data: A dictionary containing activity details to be upserted.

        :return: The number of rows inserted or updated in the activities table.
        """
        logger.debug("Upserting activity with ID %s", activity_data.get("activity_id"))
        async with self.db_service.get_async_session() as session:
            try:
                stmt = (
                    insert(Activity)
                    .values(**activity_data)
                    .on_conflict_do_update(
                        index_elements=["activity_id"],
                        set_={
                            key: activity_data[key]
                            for key in activity_data
                            if key != "activity_id"
                        },
                    )
                )
                result = await session.execute(stmt)
                await session.commit()
                row_count = result.rowcount
                if row_count > 0:
                    logger.debug(f"Activity successfully upserted.")
                return row_count
            except Exception as e:
                await session.rollback()
                logger.error("Error upserting activity: %s", e, exc_info=True)
                return 0

    async def get_activity(self, activity_id: int) -> Activity:
        """
        Retrieves an activity by its ID from the database.

        :param activity_id: The unique identifier of the activity to retrieve.

        :return: An Activity object if found, otherwise None.
        """
        logger.info("Fetching activity with ID %s", activity_id)
        async with self.db_service.get_async_session() as session:
            try:
                result = await session.execute(
                    session.query(Activity).filter_by(activity_id=activity_id)
                )
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error("Error fetching activity: %s", e, exc_info=True)
                raise

    async def update_activity(self, activity_id: int, **kwargs) -> bool:
        """
        Updates specific fields of an activity with the specified ID.

        :param activity_id: The unique identifier of the activity to update.
        :param kwargs: Keyword arguments representing the fields to update and their new values.

        :return: True if the update was successful, False otherwise.
        """
        logger.info("Updating activity with ID %s", activity_id)
        async with self.db_service.get_async_session() as session:
            try:
                stmt = (
                    session.query(Activity)
                    .filter_by(activity_id=activity_id)
                    .update()
                    .values(**kwargs)
                )
                await session.execute(stmt)
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                logger.error("Error updating activity: %s", e, exc_info=True)
                return False

    async def delete_activity(self, activity_id: int) -> bool:
        """
        Deletes an activity by its ID from the database.

        :param activity_id: The unique identifier of the activity to delete.

        :return: True if the deletion was successful, False otherwise.
        """
        logger.info("Deleting activity with ID %s", activity_id)
        async with self.db_service.get_async_session() as session:
            try:
                stmt = (
                    session.query(Activity).filter_by(activity_id=activity_id).delete()
                )
                await session.execute(stmt)
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                logger.error("Error deleting activity: %s", e, exc_info=True)
                return False

    # TODO - JACOB: Continue working on this. Think through it more and write up SQL query, then convert to SQLAlchemy query.
    async def get_basic_stats(self):
        """
        Gets the basic stats, representing the current week's training, for each authenticated athlete.

        Basic stats include:
        - Tallied mileage
        - Tallied moving time
        - # of runs
        - Average mileage per run
        - Average moving time per run
        - Average pace (in minutes per mile) per run
        - Longest run
        - Date of the longest run

        :return: A dictionary containing basic recap stats grouped by athlete.
        """
        logger.info("Fetching basic stats for all authenticated athletes")
        async with self.db_service.get_async_session() as session:
            try:
                # TODO: Figure out how to work with the time-based metrics
                return  # temporary return
            except Exception as e:
                logger.error(f"Error fetching basic stats: {e}")
                raise

    async def get_detailed_activities(self) -> list[Activity] | None:
        """
        Acquires a list of all detailed activities from the database to display on the "Database" page.

        :return: A list of Activity objects if successful, None otherwise.
        """
        logger.info("Acquiring a list of detailed activities")
        async with self.db_service.get_async_session() as session:
            try:
                query_result = await session.execute(session.query(Activity))
                return query_result.all()
            except Exception as e:
                logger.error(f"Error acquiring the list of detailed activities: {e}")
                return None
