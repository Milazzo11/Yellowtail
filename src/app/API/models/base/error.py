"""
HTTP error data packet model.

:author: Max Milazzo
"""


from app.error.errors import DomainException

from pydantic import BaseModel, Field
from typing import Self



class ErrorResponse(BaseModel):
    """
    HTTP error response.
    """

    error: bool = Field(..., description="Error status")
    detail: str = Field(..., description="Error detail")


    @classmethod
    def generate(cls, exception: DomainException) -> Self:
        """
        Generate HTTP error response.

        :param exception: HTTP exception
        :return: error response
        """

        detail = exception.message

        return cls(error=True, detail=detail)