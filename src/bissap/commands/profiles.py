import sqlite3

import click

from bissap.commands.common import build_by_authorization, group
from bissap.db import select_first
from bissap.globals import json_output, json_print
from bissap.logging import get_logger
from bissap.profiles import (
    extract_profile,
    get_detailed_profiles_of_role,
    get_detailed_profiles_of_user,
)

log = get_logger(__name__)


@group()
def profiles():
    """List profiles assigned to a user or with a specific authorization."""


@profiles.command()
@click.argument('role')
@click.option('--verbose', '-v', is_flag=True)
def of_role(role: str, verbose: bool):
    profiles = get_detailed_profiles_of_role(role)
    _print_results(profiles, verbose)


@profiles.command()
@click.argument('user')
@click.option('--verbose', '-v', is_flag=True)
def of_user(user: str, verbose: bool):
    profiles = get_detailed_profiles_of_user(user)
    _print_results(profiles, verbose)


def _print_results(
    profiles: dict[str, dict[str, dict[str, list[tuple[str, str, str]]]]], verbose: bool
):
    """
    Display the results of `get_assigned_profiles_of` and other similar functions.
    """

    if json_output():
        if not verbose:
            json_print(profiles.keys())
        else:
            json_print(profiles)
        return

    if not verbose:
        for profile in profiles.keys():
            print(profile)
        return

    for profile_name, objects in profiles.items():
        print(f'{profile_name}')
        for object_name, auths in objects.items():
            print(f'  {object_name}')
            for auth_name, fields in auths.items():
                for field_name, von, bis in fields:
                    summary = f'{auth_name}:'
                    range = f'({von},{bis})'
                    if not bis:
                        range = f'({von})'
                    summary += f' {field_name}{range}'

                    if (
                        object_name == 'S_SERVICE'
                        and field_name == 'SRV_NAME'
                        and not bis
                    ):
                        summary += f' = {_resolve_srv_name(von)}'
                    print(f'    {summary}')


def _resolve_srv_name(srv_name: str):
    """
    Convert a SRV_NAME value from a S_SERVICE authorization to its true value.
    According to SAP:
    > This is a hashed value. Each service has its own hash value, that is, you can restrict the access to the system on system level.
    > If you need the linkage of hash value to object catalog entry, refer to table USOBHASH.
    """

    try:
        res: tuple[str] | None = select_first(
            'SELECT OBJ_NAME FROM USOBHASH WHERE NAME=?', (srv_name,)
        )

        return res[0] if res else ''
    except sqlite3.OperationalError:
        return ''


build_by_authorization(log, profiles, extract_profile)
