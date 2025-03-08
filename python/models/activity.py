from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    Time,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    BigInteger,
)

# Use the Athlete model's Base
from .athlete import Base


class Activity(Base):
    """
    Represents a single Strava run activity corresponding to the 'activities' database table.
    """

    __tablename__ = "activities"
    __table_args__ = {"schema": "strava_api"}  # To use the `strava_api` schema

    # Primary and foreign keys
    activity_id = Column(BigInteger, primary_key=True, autoincrement=False)
    athlete_id = Column(
        BigInteger, ForeignKey("strava_api.athletes.athlete_id"), nullable=False
    )

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

    def __repr__(self):
        return (
            f"<Activity(activity_id={self.activity_id}, athlete={self.athlete}, "
            f"distance_mi={self.distance_mi}, moving_time={self.moving_time})>"
        )

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
        - moving_time (TIME, NOT NULL): Time spent moving (HH:MM:SS).
        - moving_time_s (INTEGER, NOT NULL): Moving time in seconds.
        - distance_mi (FLOAT, NOT NULL): Distance covered in miles.
        - pace_min_mi (TIME, NULL): Average pace in minutes per mile.
        - avg_speed_ft_s (FLOAT(2), NOT NULL): Average speed in feet per second.
        - full_datetime (DATETIME, NULL): Full timestamp of the activity.
        - time (TIME, NOT NULL): Time of day when the activity took place.
        - week_day (STRING, NOT NULL): Day of the week (e.g., MON-SUN).
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
        
        Notes: 
        - Primary Key: activity_id
        - Foreign Key: athlete_id references strava_api.athletes.athlete_id
        - The 'wkt_type' column, regardless of the value, represents a run of some form.
            - If a user asks for a specific type of run, consider filtering by this column in the SQL generation. Otherwise, ignore it.
        """

        return schema_description.strip()
