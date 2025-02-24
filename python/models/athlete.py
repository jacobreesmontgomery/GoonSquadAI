from sqlalchemy import Column, BigInteger, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Athlete(Base):
    """
    Represents a single Strava athlete corresponding to the 'athlete' database table.
    """

    __tablename__ = "athletes"
    __table_args__ = {"schema": "strava_api"}  # Schema defined as `strava_api`

    # Primary key
    athlete_id = Column(BigInteger, primary_key=True, autoincrement=False)

    # Athlete details
    athlete_name = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return (
            f"<Athlete(athlete_id={self.athlete_id}, athlete_name={self.athlete_name}, "
            f"email={self.email})>"
        )

    def convert_to_schema_description(self):
        """
        Converts the Athlete SQLAlchemy model to an LLM-interpretable schema description.
        """

        schema_description = f"""
        Table: strava_api.athletes
        Description: This table stores information about Strava athletes, including their identifiers, 
        authentication tokens, and contact details.

        Columns:
        - athlete_id (BIGINT, PK): Unique identifier for the athlete.
        - athlete_name (STRING, NOT NULL): Name of the athlete.
        - refresh_token (STRING, NOT NULL): OAuth refresh token for authentication.
        - email (STRING, UNIQUE, NOT NULL): Athlete's email address (must be unique).

        Notes:
        - Primary Key: athlete_id
        """

        return schema_description.strip()
