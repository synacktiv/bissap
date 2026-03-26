from functools import lru_cache

from bissap.db import select_all
from bissap.globals import client


def extract_username(user: tuple[str, ...]):
    return user[0]


@lru_cache()
def all_users_name_with_profile(profile_name: str):
    """
    Return all users with an assigned profile.
    """
    users: list[tuple[str]] = select_all(
        'SELECT BNAME FROM UST04 WHERE MANDT=? AND PROFILE=?',
        (client(), profile_name),
    )

    return [bname for (bname,) in users]


def all_users_name_with_role(role_name: str):
    """
    Return all users with an effective profile.
    """
    users: list[tuple[str]] = select_all(
        'SELECT DISTINCT(UNAME) FROM AGR_USERS WHERE AGR_NAME=? AND MANDT=?',
        (role_name, client()),
    )

    return [bname for (bname,) in users]


def all_users_name():
    """
    Return all non-locked users.
    """
    users: list[tuple[str]] = select_all(
        'SELECT BNAME FROM USR02 WHERE UFLAG="0" AND ZBVMASTER != "X" AND MANDT=?',
        (client(),),
    )
    return [bname for (bname,) in users]
