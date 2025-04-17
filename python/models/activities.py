from pydantic import BaseModel, validator
from typing import Any, Optional
from enum import Enum

from .athlete import Activity as DBActivity


class DetailedActivities(BaseModel):
    headers: list[str]
    activities: list[dict[str, Any]]

    @classmethod
    def model_validate(
        cls, detailed_activities: list[DBActivity]
    ) -> "DetailedActivities":
        """
        Validates the DetailedActivities model.

        :param data: The data to validate.

        :return: The validated DetailedActivities model.
        """

        headers = list(
            {
                key
                for activity in detailed_activities
                for key in activity.__dict__.keys()
            }
        )

        return cls(
            headers=headers,
            activities=[activity.__dict__ for activity in detailed_activities],
        )


class UpdateDatabaseActivitiesRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: Optional[int] = None
    athlete_ids: Optional[list[int]] = None

    @validator("athlete_ids")
    def validate_athlete_ids(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError("athlete_ids cannot be an empty list")
        return v


class UpdatedAthleteActivities(BaseModel):
    athlete_id: int
    num_updated_activities: int

    @classmethod
    def model_validate(
        cls, athlete_id: int, num_updated_activities: int
    ) -> "UpdatedAthleteActivities":
        """
        Validates the UpdatedAthleteActivities model.

        :param data: The data to validate.

        :return: The validated UpdatedAthleteActivities model.
        """

        return cls(athlete_id=athlete_id, num_updated_activities=num_updated_activities)


class AllUpdatedActivities(BaseModel):
    updated_activities: list[UpdatedAthleteActivities]
