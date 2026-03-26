from bissap.db import does_table_exist, select_all, select_first
from bissap.globals import client
from bissap.logging import get_logger

log = get_logger(__name__)


def get_detailed_profiles_of_user(bname: str):
    """
    List all effectives profiles of a user with authorization details.
    """

    assigned_profiles = get_profiles_of_user(bname)

    profiles: dict[str, dict[str, dict[str, list[tuple[str, str, str]]]]] = {}
    for profile in assigned_profiles:
        profiles[profile] = get_details_of_profile(profile)

    return profiles


def get_profiles_of_user(bname: str):
    """
    List all profiles assigned to a user.
    """

    res: list[tuple[str]] = select_all(
        """
        SELECT DISTINCT PROFILE
        FROM UST04 WHERE MANDT=? AND BNAME=?
        """,
        (client(), bname),
    )

    return {prof for (prof,) in res}


def get_profiles_of_role(role_name: str):
    res: list[tuple[str]] = select_all(
        """
        SELECT DISTINCT PROFILE
        FROM AGR_PROF WHERE MANDT=? AND AGR_NAME=?
        """,
        (client(), role_name),
    )

    return {prof for (prof,) in res}


def get_detailed_profiles_of_role(role_name: str):
    """
    List all profiles of a role with authorization details.
    """

    assigned_profiles = get_profiles_of_role(role_name)

    profiles: dict[str, dict[str, dict[str, list[tuple[str, str, str]]]]] = {}
    for profile in assigned_profiles:
        profiles[profile] = get_details_of_profile(profile)

    return profiles


def get_details_of_profile(profile: str):
    raw: list[tuple[str, str, str, str, str]] = select_all(
        """
        SELECT DISTINCT OBJCT, AUTH, FIELD, VON, BIS 
        FROM PROFILE_AUTHS WHERE MANDT=? AND ROOTPROFN=?
        """,
        (client(), profile),
    )

    objects: dict[str, dict[str, list[tuple[str, str, str]]]] = {}
    for objct, auth, field, von, bis in raw:
        objct_dict = objects.setdefault(objct, {})
        auth_dict = objct_dict.setdefault(auth, [])
        auth_dict.append((field, von, bis))

    return objects


def extract_profile(user: tuple[str, ...]):
    return user[1]


def does_profile_exist(profile: str):
    """
    Opportunistically Check if the provided profile exists.
    If the profile master table (USR11) is not present, returns True by default.
    """

    if not does_table_exist('USR11'):
        return True

    return (
        select_first(
            "SELECT 1 FROM USR11 WHERE MANDT=? AND AKTPS='A' AND PROFN=?",
            (client(), profile),
        )
        is not None
    )
