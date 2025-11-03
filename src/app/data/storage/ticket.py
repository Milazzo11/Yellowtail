import sqlite3
import pickle
from config import DB_FILE

from typing import List

### TODO * transfer table

### TODO - abstract out SQLite specifically
### TODO* cursor.execute("BEGIN IMMEDIATE") in front of everything


BYTE_SIZE = 8
# assumed byte size (in bits)

## TODO* maybe make byte size global







### TODO * gotta add "issued #" to all of these and incorporate in final checks











def _redeem_check(cursor):
    # Fetch the redemption bitstring for the event
    cursor.execute("""
        SELECT redeemed_bitstring FROM event_data
        WHERE event_id = ?
    """, (event_id,))
    row = cursor.fetchone()

    redeemed_bitstring = bytearray(row[0])
    ticket_mask = 1 << (ticket_number % 8)

    if redeemed_bitstring[ticket_number // BYTE_SIZE] & ticket_mask != 0:
        return True

    return False





def _transfer_valid_checker(event_id: str, ticket_number: int, version: int) -> bool:
    """
    Validates ticket ownership (to prevent transfer fraud attempts).
    """
    ## called from ./../ticket.load and reissue prob



def transfer_valid_check(event_id: str, ticket_number: int, version: int) -> bool:
    """
    Validates ticket ownership (to prevent transfer fraud attempts).
    """
    ## called from ./../ticket.load and reissue prob

    cur.execute("""
        SELECT * FROM transfer_log
        WHERE event_id = ?
            AND ticket_number = ?
            AND version = ?
    """, (event_id, ticket_number, version))

    if cur.rowcount == 1:
        return True

    return False


def reissue(event_id: str, ticket_number: int, version: int) -> None:
    """
    """
    ### TODO*** this should happen here but with sql clause to prevent rare fraud-induced race condition

    ## atomic w/ race cond prevention

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE transfer_log
        SET version = version + 1
        WHERE event_id = ?
            AND ticket_number = ?
            AND version = ?
    """, (event_id, ticket_number, version))

    if cursor.rowcount != 1:
        raise HTTPException(409, "Transfer concurrency race condition detected")

    conn.commit()
    conn.close()





REDEEMED_BYTE = 255

def verify(event_id: str, ticket_number: int) -> bool:
    """
    Verifies ticket redemption: return True if redeemed, else False.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Read exactly one byte (SQLite substr is 1-based)
    cur.execute("""
        SELECT substr(data_bytes, ?, 1)
        FROM event_data
        WHERE event_id = ?
    """, (ticket_number + 1, event_id))
    row = cur.fetchone()
    conn.close()

    # If row exists, row[0] is a bytes object of length 1
    return row[0][0] == REDEEMED_BYTE



def redeem(event_id: str, ticket_number: int) -> bool:
    """
    Mark the ticket as redeemed (set its byte to 0xFF) only if not already redeemed.

    :returns: True if this is a new redemption, False if it had been redeemed before.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Splice in a single byte (0xFF) only if the current byte is not already 0xFF.
    # If another writer redeems concurrently, this UPDATE affects 0 rows and we return False.
    cur.execute("""
        UPDATE event_data
           SET data_bytes =
                substr(data_bytes, 1, ?) || x'FF' || substr(data_bytes, ? + 2)
         WHERE event_id = ?
           AND substr(data_bytes, ?, 1) <> x'FF'
    """, (ticket_number, ticket_number, event_id, ticket_number + 1))

    changed = (cur.rowcount == 1)

    if changed:
        conn.commit()

    conn.close()
    return changed