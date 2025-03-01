from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing import Any, TypeVar, Generic, Union, Dict

DataT = TypeVar("DataT")
MetaT = TypeVar("MetaT")


class Empty(BaseModel):
    """
    A model representing an empty object.
    """

    pass


class APIResponsePayload(GenericModel, Generic[DataT, MetaT]):
    """
    A model representing the payload of an API response.

    :param data: The data of the response.
    :param meta: The metadata of the response.
    """

    data: DataT
    meta: MetaT | Empty = Empty()
