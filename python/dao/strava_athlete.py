from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select

from models.athlete import Athlete
from services.database import DatabaseService
from utils.simple_logger import SimpleLogger

logger = SimpleLogger(class_name=__name__).logger


class StravaAthleteDao:
    """
    Responsible for managing athlete data in the database.
    """

    def __init__(self, db_service: DatabaseService = DatabaseService()):
        self.db_service = db_service

    async def upsert_athlete(
        self, athlete_id: int, athlete_name: str, refresh_token: str, email: str
    ) -> int:
        """
        Inserts or updates an athlete in the database (upsert).

        Args:
            athlete_id: The athlete's ID.
            athlete_name: The name of the athlete.
            refresh_token: The refresh token for the athlete.
            email: The email of the athlete.

        Returns:
            The athlete's ID after the upsert operation.
        """
        logger.info("Upserting athlete with ID %s", athlete_id)
        async with self.db_service.get_async_session() as session:
            try:
                stmt = (
                    insert(Athlete)
                    .values(
                        athlete_id=athlete_id,
                        athlete_name=athlete_name,
                        refresh_token=refresh_token,
                        email=email,
                    )
                    .on_conflict_do_update(
                        index_elements=[
                            "athlete_id"
                        ],  # Conflict target (e.g., primary key)
                        set_={
                            "athlete_name": athlete_name,
                            "refresh_token": refresh_token,
                            "email": email,
                        },
                    )
                )
                result = await session.execute(stmt)
                await session.commit()
                row_count = result.rowcount
                logger.info(f"{row_count} rows were updated")
                return row_count
            except Exception as e:
                await session.rollback()
                logger.error("Error upserting athlete: %s", e, exc_info=True)
                return 0

    async def get_athlete(self, athlete_id: int) -> Athlete:
        """
        Retrieves an athlete by their ID.

        Args:
            athlete_id: The athlete's ID.

        Returns:
            An Athlete object (or None if not found).
        """
        logger.info("Fetching athlete with ID %s", athlete_id)
        async with self.db_service.get_async_session() as session:
            try:
                stmt = select(Athlete).where(Athlete.athlete_id == athlete_id)
                result = await session.execute(stmt)
                return result.scalars().first()
            except NoResultFound:
                logger.warning("No athlete found with ID %s", athlete_id)
                return None
            except Exception as e:
                logger.error("Error getting athlete: %s", e, exc_info=True)
                raise

    async def get_athlete_id(self, athlete_name: str) -> int:
        """
        Retrieves an athlete's ID by their name.

        Args:
            athlete_name: The name of the athlete.

        Returns:
            An int representing the athlete's ID (or None if not found).
        """
        logger.info("Fetching athlete ID for '%s'", athlete_name)
        async with self.db_service.get_async_session() as session:
            try:
                stmt = select(Athlete).where(Athlete.athlete_name == athlete_name)
                result = await session.execute(stmt)
                athlete: Athlete = result.scalars().first()
                if athlete:
                    logger.info(
                        f"Acquired athlete ID of {athlete.athlete_id} for {athlete_name}"
                    )
                    return athlete.athlete_id
                logger.info("No athlete ID was found.")
                return None
            except Exception as e:
                logger.error("Error getting athlete ID: %s", e, exc_info=True)
                raise

    async def get_all_authenticated_athletes(self) -> list[Athlete]:
        """
        Retrieves all authenticated athletes from the database.

        Returns:
            A list of Athlete objects.
        """
        logger.info("Fetching all athletes")
        async with self.db_service.get_async_session() as session:
            try:
                stmt = select(Athlete)
                result = await session.execute(stmt)
                return result.scalars().all()
            except Exception as e:
                logger.error("Error getting athletes: %s", e, exc_info=True)
                raise

    async def update_athlete(
        self,
        athlete_id: int,
        athlete_name: str = None,
        refresh_token: str = None,
        email: str = None,
    ) -> bool:
        """
        Updates an athlete's details in the database.

        Args:
            athlete_id: The athlete's ID.
            athlete_name: The new name for the athlete.
            refresh_token: The new refresh token for the athlete.
            email: The new email for the athlete.

        Returns:
            A boolean indicating whether or not the athlete's details were updated.
        """
        logger.info("Updating athlete with ID %s", athlete_id)
        async with self.db_service.get_async_session() as session:
            try:
                stmt = select(Athlete).where(Athlete.athlete_id == athlete_id)
                result = await session.execute(stmt)
                athlete: Athlete = result.scalars().first()

                if not athlete:
                    logger.warning("No athlete found with ID %s", athlete_id)
                    return False

                if athlete_name:
                    athlete.athlete_name = athlete_name
                if refresh_token:
                    athlete.refresh_token = refresh_token
                if email:
                    athlete.email = email

                await session.commit()
                logger.info("Athlete with ID %s updated", athlete_id)
                return True
            except Exception as e:
                await session.rollback()
                logger.error("Error updating athlete: %s", e, exc_info=True)
                return False

    async def delete_athlete(self, athlete_id: int) -> bool:
        """
        Deletes an athlete from the database.

        Args:
            athlete_id: The athlete's ID.

        Returns:
            A boolean indicating whether or not the athlete was deleted.
        """
        logger.info("Deleting athlete with ID %s", athlete_id)
        async with self.db_service.get_async_session() as session:
            try:
                stmt = select(Athlete).where(Athlete.athlete_id == athlete_id)
                result = await session.execute(stmt)
                athlete: Athlete = result.scalars().first()

                if not athlete:
                    logger.warning("No athlete found with ID %s", athlete_id)
                    return False

                await session.delete(athlete)
                await session.commit()
                logger.info("Athlete with ID %s deleted", athlete_id)
                return True
            except Exception as e:
                await session.rollback()
                logger.error("Error deleting athlete: %s", e, exc_info=True)
                return False
