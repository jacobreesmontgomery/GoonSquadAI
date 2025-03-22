from pydantic import BaseModel
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


class UpdatedActivities(BaseModel):
    num_updated_activities: int
