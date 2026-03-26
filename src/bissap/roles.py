from bissap.db import does_table_exist, select_all, select_first
from bissap.globals import client
from bissap.logging import get_logger

log = get_logger(__name__)


def get_role_with_profile(profile_name: str):
    """
    Return the role containing the provided profile, if it exists.

    It assumes that at most one role will exist.
    """

    role: tuple[str] | None = select_first(
        'SELECT AGR_NAME FROM AGR_1016 WHERE MANDT=? AND PROFILE=?',
        (client(), profile_name),
    )

    return role[0] if role else None


def get_roles_of_user(bname: str):
    """
    List all roles of a user.
    """

    roles: list[tuple[str]] = select_all(
        'SELECT AGR_NAME FROM AGR_USERS WHERE MANDT=? AND UNAME=?',
        (client(), bname),
    )

    return [role for (role,) in roles]


def get_role_description(role_name: str):
    """
    Return the description of the specified role.
    Locale is not respected. The first description, regardless of language, found in the DB is returned.
    """

    res: tuple[str] | None = select_first(
        'SELECT TEXT FROM AGR_TEXTS WHERE MANDT=? AND AGR_NAME=?',
        (client(), role_name),
    )

    return res[0] if res else ''


def get_all_assigned_roles():
    """
    Return all roles with at least one user assigned.
    """

    res: list[tuple[str]] = select_all('SELECT DISTINCT AGR_NAME FROM AGR_USERS')

    return {role for (role,) in res}


def extract_role(user: tuple[str, ...]):
    return user[2]


def does_role_exist(role: str):
    """
    Opportunistically Check if the provided role exists.
    If the role master table (AGR_DEFINE) is not present, returns True by default.
    """

    if not does_table_exist('AGR_DEFINE'):
        return True

    return (
        select_first(
            'SELECT 1 FROM AGR_DEFINE WHERE MANDT=? AND AGR_NAME=?',
            (client(), role),
        )
        is not None
    )
