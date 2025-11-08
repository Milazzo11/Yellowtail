"""
API endpoints
"""

from app.API import API
from app.API.models import *

from app.error.errors import ErrorKind, DomainException
from app.error.logger import log
from app.error.map import HTTP_CODE

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


app = FastAPI()


@app.post("/search", description="Search for events")
async def search_events(data: Auth[SearchRequest]) -> Auth[SearchResponse]:
    return API.search_events(data)


@app.post("/create", description="Create a new event on the server")
async def create_event(data: Auth[CreateRequest]) -> Auth[CreateResponse]:
    return API.create_event(data)


@app.post("/register", description="Register a user for an event and return his ticket")
async def register_user(data: Auth[RegisterRequest]) -> Auth[RegisterResponse]:
    return API.register_user(data)


@app.post(
    "/transfer",
    description="Return a ticket back to the server or transfer it to another user",
)
async def transfer_ticket(data: Auth[TransferRequest]) -> Auth[TransferResponse]:
    return API.transfer_ticket(data)


@app.post("/redeem", description="Redeem a ticket")
async def redeem_ticket(data: Auth[RedeemRequest]) -> Auth[RedeemResponse]:
    return API.redeem_ticket(data)


@app.post("/verify", description="Verify that a user has redeemed his ticket")
async def verify_redemption(data: Auth[VerifyRequest]) -> Auth[VerifyResponse]:
    return API.verify_redemption(data)


@app.post("/delete", description="Delete an event")
async def delete_event(data: Auth[DeleteRequest]) -> Auth[DeleteResponse]:
    return API.delete_event(data)


@app.exception_handler(DomainException)
async def handle_domain_error(_: Request, exception: DomainException) -> JSONResponse:
    if exception.kind == ErrorKind.INTERNAL:
        log(str(exception))

    auth_error = API.exception_handler(exception)

    return JSONResponse(
        status_code=HTTP_CODE[exception.kind],
        content=auth_error.model_dump()
    )


@app.exception_handler(Exception)
async def exception_handler(_: Request, exception: Exception) -> JSONResponse:
    log(str(exception))

    auth_error = API.exception_handler(
        DomainException(
            kind=ErrorKind.INTERNAL,
            message="unknwon error"
        )
    )

    return JSONResponse(
        status_code=HTTP_CODE[ErrorKind.INTERNAL],
        content=auth_error.model_dump()
    )