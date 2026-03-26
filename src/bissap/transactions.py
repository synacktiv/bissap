from bissap.db import select_all
from bissap.globals import client


def all_transactions_by_usage():
    """
    Return all transactions and their associated programs, sorted by the number of users allowed to execute it.
    """

    query = """
        SELECT COUNT(*) AS POPULARITY, VON AS TCODE, (
            SELECT PGMNA FROM TSTC WHERE TSTC.TCODE = VON LIMIT 1
        ) as PROGNAME
        FROM PROFILE_AUTHS  WHERE MANDT=? AND OBJCT="S_TCODE" GROUP BY VON ORDER BY POPULARITY DESC
    """
    transactions: list[tuple[int, str, str]] = select_all(query, (client(),))

    return transactions
