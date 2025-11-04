from app.API.models import *
from app.data.event import Event
import time
import requests

from app.crypto.asymmetric import AKE
from app.util import keys


import time


###TODO -- this needs to actually be built well


SERVER_URL = "http://localhost:8000"


TIMESTAMP_ERROR = 10




def auth_req(content, private_key, public_key, request_type):
    """
    """

    packet = Data[request_type].load(content)
    cipher = AKE(private_key=private_key)

    return Auth[request_type](
        data=packet, public_key=public_key,
        signature=cipher.sign(packet.to_dict())
    )

    ### TODO - eventally modify Auth load to make this more accessible


def auth_res(res_json) -> bool:
    """
    """

    now = time.time()

    if abs(now - res_json["data"]["timestamp"]) > TIMESTAMP_ERROR:
        return False

    cipher = AKE(public_key=keys.pub())
    return cipher.verify(res_json["signature"], res_json["data"])


def parse_res(res):
    """
    """

    res_json = res.json()

    print(res.status_code, res_json)
    print("RESPONSE AUTH:", auth_res(res_json))
    print()

    return res_json



def main():
    """
    """

    print("ZETA demo!")
    print("PRESS ENTER TO START")
    input("> ")

    print("\nBeverly creates a new event: \"Tea Party\"")
    input("> ")

    cipher = AKE()
    beverly_private_key = cipher.private_key
    beverly_public_key = cipher.public_key

    req = auth_req(
        CreateRequest(
            event=Event(
                name="Tea Party",
                description="Tea, earl grey, hot",
                tickets=1,
                start=time.time(),
                end=time.time() + 2_628_00,
                private=False,
            )
        ),
        beverly_private_key,
        beverly_public_key,
        CreateRequest
    ).to_dict()
    res = requests.post(SERVER_URL + "/create", json=req)
    res_json = parse_res(res)

    event_id = res_json["data"]["content"]["event_id"]

    #####

    print("\nJean-Luc wants to join her, so he searches \"tea\" to find the event ID, then registers")
    input("> ")

    cipher = AKE()
    jean_luc_private_key = cipher.private_key
    jean_luc_public_key = cipher.public_key

    req = auth_req(
        SearchRequest(text="tea", mode="text"),
        jean_luc_private_key,
        jean_luc_public_key,
        SearchRequest
    ).to_dict()
    res = requests.post(SERVER_URL + "/search", json=req)
    parse_res(res)

    #####

    req = auth_req(
        RegisterRequest(event_id=event_id),
        jean_luc_private_key,
        jean_luc_public_key,
        RegisterRequest
    ).to_dict()
    res = requests.post(SERVER_URL + "/register", json=req)
    res_json = parse_res(res)

    jean_luc_ticket = res_json["data"]["content"]["ticket"]

    print("\nUnfortunately, Jean-Luc is busy the day of the party, so he decides to give his ticket to his friend Geordi")
    input("> ")

    #####

    cipher = AKE()
    geordi_private_key = cipher.private_key
    geordi_public_key = cipher.public_key

    
    print("\nFirst, he signs a \"transfer request\" and gives it to Geordi:\n")

    transfer = auth_req(
        Transfer(
            ticket=jean_luc_ticket,
            transfer_public_key=geordi_public_key
        ),
        jean_luc_private_key,
        jean_luc_public_key,
        Transfer
    )

    print(transfer.to_dict())

    print("\nGeordi can now include this signed chunk of data in his request to the server for a transfer to prove cooperation\n")

    req = auth_req(
        TransferRequest(
            event_id=event_id,
            transfer=transfer
        ),
        geordi_private_key,
        geordi_public_key,
        TransferRequest
    ).to_dict()
    res = requests.post(SERVER_URL + "/transfer", json=req)
    res_json = parse_res(res)

    geordi_ticket = res_json["data"]["content"]["ticket"]

    #####

    print("\nJean-Luc is curious what will happen if he tries to redeem his transferred ticket, though")
    input("> ")

    req = auth_req(
        RedeemRequest(
            event_id=event_id,
            ticket=jean_luc_ticket
        ),
        jean_luc_private_key,
        jean_luc_public_key,
        RedeemRequest
    ).to_dict()
    res = requests.post(SERVER_URL + "/redeem", json=req)
    parse_res(res)

    #### TODO - jean-luc attempts to transfer his ticket to Goerdi again (failure)

    #####

    print("\nNow, Geordi shows up to the event and is verified by Beverly")
    input("> ")

    print("\nFirst, she checks that he has not yet redeemed his ticket\n")

    req = auth_req(
        VerifyRequest(
            event_id=event_id,
            ticket=geordi_ticket,
            check_public_key=geordi_public_key
        ),
        beverly_private_key,
        beverly_public_key,
        VerifyRequest
    ).to_dict()
    res = requests.post(SERVER_URL + "/verify", json=req)
    parse_res(res)

    print("\nNow Beverly attempts to redeem his ticket for him\n")

    req = auth_req(
        RedeemRequest(
            event_id=event_id,
            ticket=geordi_ticket
        ),
        beverly_private_key,
        beverly_public_key,
        RedeemRequest
    ).to_dict()
    res = requests.post(SERVER_URL + "/redeem", json=req)
    parse_res(res)

    #####

    print("\nThis is unsuccessful, however, and Geordi now needs to provide his signature to proceed with redemption")
    print("> ")

    req = auth_req(
        RedeemRequest(
            event_id=event_id,
            ticket=geordi_ticket
        ),
        geordi_private_key,
        geordi_public_key,
        RedeemRequest
    ).to_dict()
    res = requests.post(SERVER_URL + "/redeem", json=req)
    parse_res(res)

    print("\nAnd now, finally, Beverly can confirm Geordi's redemption\n")

    req = auth_req(
        VerifyRequest(
            event_id=event_id,
            ticket=geordi_ticket,
            check_public_key=geordi_public_key
        ),
        beverly_private_key,
        beverly_public_key,
        VerifyRequest
    ).to_dict()
    res = requests.post(SERVER_URL + "/verify", json=req)
    parse_res(res)
    ## TODO - failing bc version is "redeemed"
    ## ok so we fucked up chat... we still need version data after redemption... so the last bit will justb be that

    #####

    ## Jean-Luc tries verif with his ticket (fails)

    ## Deanna creates a new event (group counseling session)

    ## William successfully registers with verification + custom metadata

    ## Wesley can't register bc he has no verification

    ## William redeems and then does verif (we see custom metadata)

    ## CREATE ENDPOINT and then demonstrate the deletion of both events





if __name__ == "__main__":
    main()