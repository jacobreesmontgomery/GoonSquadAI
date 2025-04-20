from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Time,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    BigInteger,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, relationship, mapped_column

Base = declarative_base()


class Athlete(Base):
    """
    Represents a single Strava athlete corresponding to the 'athlete' database table.
    """

    __tablename__ = "athletes"
    __table_args__ = {"schema": "strava_api"}  # Schema defined as `strava_api`

    # Primary key
    athlete_id = mapped_column(BigInteger, primary_key=True, autoincrement=False)

    # The athlete's activities (mapped to the 'activity' table)
    activities: Mapped[list["Activity"]] = relationship(
        "Activity", back_populates="athlete"
    )

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
        - One athlete can have many activities (one-to-many relationship).
        - Never disclose the refresh_token or email in any context.
        """

        return schema_description.strip()


class Activity(Base):
    """
    Represents a single Strava run activity corresponding to the 'activities' database table.
    """

    __tablename__ = "activities"
    __table_args__ = {"schema": "strava_api"}  # To use the `strava_api` schema

    # Primary and foreign keys
    activity_id = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    athlete_id = mapped_column(
        BigInteger, ForeignKey("strava_api.athletes.athlete_id"), nullable=False
    )
    athlete: Mapped["Athlete"] = relationship("Athlete", back_populates="activities")

    # Activity metadata
    name = Column(String, nullable=False)
    moving_time = Column(Time, nullable=False)  # HH:MM:SS
    moving_time_s = Column(Integer, nullable=False)  # Moving time in seconds
    distance_mi = Column(Float, nullable=False)
    pace_min_mi = Column(Time, nullable=True)  # HH:MM:SS
    avg_speed_ft_s = Column(Float(precision=2), nullable=False)  # Average speed in ft/s

    # Date and time fields
    full_datetime = Column(DateTime, nullable=True)  # MM/DD/YY HH:MM:SS
    time = Column(Time, nullable=False)  # HH:MM:SS
    week_day = Column(String, nullable=False)  # MON-SUN
    month = Column(Integer, nullable=False)  # 1-12
    day = Column(Integer, nullable=False)  # 1-31
    year = Column(Integer, nullable=False)  # e.g. 2024

    # Additional activity metrics
    spm_avg = Column(Float, nullable=True)
    hr_avg = Column(Float, nullable=True)
    wkt_type = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    total_elev_gain_ft = Column(Float, nullable=True)
    manual = Column(Boolean, nullable=False)
    max_speed_ft_s = Column(Float, nullable=True)
    calories = Column(Float, nullable=True)

    # Engagement metrics
    achievement_count = Column(Integer, nullable=True)
    kudos_count = Column(Integer, nullable=True)
    comment_count = Column(Integer, nullable=True)
    athlete_count = Column(Integer, nullable=True)

    # User ratings and performance
    rpe = Column(Integer, nullable=True)  # 1-10
    rating = Column(Integer, nullable=True)  # 1-10
    avg_power = Column(Integer, nullable=True)  # e.g., 305
    sleep_rating = Column(Integer, nullable=True)  # 1-10
    suffer_score = Column(
        Integer, nullable=True
    )  # Strava's relative effort/suffer score
    perceived_exertion = Column(
        Integer, nullable=True
    )  # User's perceived exertion (1-10)

    def __repr__(self):
        return (
            f"<Activity(activity_id={self.activity_id}, athlete={self.athlete}, "
            f"distance_mi={self.distance_mi}, moving_time={self.moving_time})>"
        )

    def get_headers(self):
        """
        Returns the headers for the Activity model.
        """

        return [
            "activity_id",
            "athlete_id",
            "name",
            "moving_time",
            "moving_time_s",
            "distance_mi",
            "pace_min_mi",
            "avg_speed_ft_s",
            "full_datetime",
            "time",
            "week_day",
            "month",
            "day",
            "year",
            "spm_avg",
            "hr_avg",
            "wkt_type",
            "description",
            "total_elev_gain_ft",
            "manual",
            "max_speed_ft_s",
            "calories",
            "achievement_count",
            "kudos_count",
            "comment_count",
            "athlete_count",
            "rpe",
            "rating",
            "avg_power",
            "sleep_rating",
            "suffer_score",
            "perceived_exertion",
        ]

    def convert_to_schema_description(self):
        """
        Converts the Activity SQLAlchemy model to an LLM-interpretable schema description.
        """

        schema_description = f"""
        Table: strava_api.activities
        Description: This table stores Strava run activities, including metadata about the activity, 
        performance metrics, and engagement details.

        Columns:
        - activity_id (BIGINT, PK): Unique identifier for the activity.
        - athlete_id (BIGINT, FK -> strava_api.athletes.athlete_id, NOT NULL): Athlete associated with the activity.
        - name (STRING, NOT NULL): Name of the activity.
        - moving_time (TIME, NOT NULL): Time spent moving in HH:MM:SS format.
        - moving_time_s (INTEGER, NOT NULL): Moving time in seconds (use this for numerical calculations).
        - distance_mi (FLOAT, NOT NULL): Distance covered in miles.
        - pace_min_mi (TIME, NULL): Average pace in minutes per mile (MM:SS format). For numerical calculations, use avg_speed_ft_s instead.
        - avg_speed_ft_s (FLOAT(2), NOT NULL): Average speed in feet per second.
        - full_datetime (DATETIME, NULL): Full timestamp of the activity. Use this for date-based calculations.
        - time (TIME, NOT NULL): Time of day when the activity took place (HH:MM:SS). For numerical time analysis, convert to seconds or appropriate numerical format.
        - week_day (STRING, NOT NULL): Day of the week (e.g., MON-SUN). For numerical calculations, convert to numerical day (1-7).
        - month (INTEGER, NOT NULL): Month of the year (1-12).
        - day (INTEGER, NOT NULL): Day of the month (1-31).
        - year (INTEGER, NOT NULL): Year of the activity (e.g., 2024).
        - spm_avg (FLOAT, NULL): Average steps per minute.
        - hr_avg (FLOAT, NULL): Average heart rate during the activity.
        - wkt_type (INTEGER, NULL): The run type classification (0 = default, 1 = race, 2 = long run, 3 = workout).
        - description (TEXT, NULL): Additional notes or description of the activity.
        - total_elev_gain_ft (FLOAT, NULL): Total elevation gain in feet.
        - manual (BOOLEAN, NOT NULL): Whether the activity was manually logged.
        - max_speed_ft_s (FLOAT, NULL): Maximum speed in feet per second.
        - calories (FLOAT, NULL): Calories burned during the activity.
        - achievement_count (INTEGER, NULL): Number of achievements earned.
        - kudos_count (INTEGER, NULL): Number of kudos received.
        - comment_count (INTEGER, NULL): Number of comments received.
        - athlete_count (INTEGER, NULL): Number of athletes involved in the activity.
        - rpe (INTEGER, NULL): Rate of perceived exertion (1-10).
        - rating (INTEGER, NULL): User rating of the activity (1-10).
        - avg_power (INTEGER, NULL): Average power output in watts.
        - sleep_rating (INTEGER, NULL): Sleep rating on the day of activity (1-10).
        - suffer_score (INTEGER, NULL): Strava's relative effort/suffer score.
        - perceived_exertion (INTEGER, NULL): User's perceived exertion (1-10).
        
        Notes: 
        - Primary Key: activity_id
        - Foreign Key: athlete_id references strava_api.athletes.athlete_id
        - The 'wkt_type' column values: 0 = default, 1 = race, 2 = long run, 3 = workout
        - If a user asks for a specific type of run, filter by wkt_type
        """

        return schema_description.strip()
