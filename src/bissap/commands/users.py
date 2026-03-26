import click

from bissap.commands.common import build_by_authorization, group
from bissap.globals import json_output, json_print
from bissap.logging import get_logger
from bissap.profiles import does_profile_exist
from bissap.roles import does_role_exist
from bissap.users import (
    all_users_name_with_profile,
    all_users_name_with_role,
    extract_username,
)

log = get_logger(__name__)


@group()
def users():
    """List users with a specific profile or authorization"""


@users.command()
@click.option('--profile', '-p', help='The profile to filter for.', required=True)
def by_profile(
    profile: str,
):
    """Filter by profile name."""
    if not does_profile_exist(profile):
        log.warning(f'Profile {profile} does not exist.')
    bnames = all_users_name_with_profile(profile)

    if json_output():
        json_print(bnames)
    else:
        for bname in bnames:
            print(bname)


@users.command()
@click.option('--role', '-r', help='The role to filter for.', required=True)
def by_role(
    role: str,
):
    """Filter by role name."""
    if not does_role_exist(role):
        log.warning(f'Role {role} does not exists.')
    bnames = all_users_name_with_role(role)

    if json_output():
        json_print(bnames)
    else:
        for bname in bnames:
            print(bname)


build_by_authorization(log, users, extract_username)
