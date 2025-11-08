"""
HTTP error data packet models.

:author: Max Milazzo
"""


from app.error.errors import DomainException

from pydantic import BaseModel, Field
from typing import Self



class Error(BaseModel):
    """
    HTTP error server response.
    """

    error: bool = Field(..., description="Error status")
    detail: str = Field(..., description="Error detail")


    @classmethod
    def generate(cls, exception: DomainException) -> Self:
        """
        Generate HTTP error server response.

        :param exception: HTTP exception
        :return: error server response
        """

        detail = exception.message

        return cls(error=True, detail=detail)