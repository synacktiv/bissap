import sqlite3
from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path

from bissap.logging import get_logger

_con: sqlite3.Connection | None = None
_cursor: sqlite3.Cursor | None = None

log = get_logger(__name__)


def init_database(db: Path):
    """
    Initialize the database
    """
    global _con, _cursor

    _con = sqlite3.connect(db)
    # _con.set_trace_callback(print)
    _cursor = _con.cursor()
    _ = _cursor.execute('PRAGMA page_size = 16384')
    _con.commit()


def select(query: str, parameters: Sequence[str] | dict[str, str]):
    assert _cursor is not None, 'Database is not initialized.'

    log.debug(query)
    log.debug(parameters)

    return _cursor.execute(query, parameters)


def select_all(query: str, parameters: Sequence[str] | dict[str, str] = ()):
    return select(query, parameters).fetchall()


def select_first(query: str, parameters: Sequence[str] | dict[str, str] = ()):
    return select(query, parameters).fetchone()


def cursor():
    assert _cursor is not None, 'Database is not initialized.'
    return _cursor


def con():
    assert _con is not None, 'Database is not initialized.'
    return _con


@lru_cache()
def is_transaction_present(tcode: str):
    """
    Return True if the transaction identified by `tcode` is installed on the system.
    """

    try:
        res: int | None = select_first('SELECT 1 FROM TSTC WHERE TCODE=?', (tcode,))
        return res is not None
    except sqlite3.OperationalError:
        # Table 'TSTC' is missing. Results may be incorrect.
        return True


def does_table_exist(table_name: str):
    res: tuple[int] = select_first(
        'SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE type="table" AND name=?)',
        (table_name,),
    )
    table_exists = bool(res[0])

    return table_exists
