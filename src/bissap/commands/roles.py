import click
from bissap.commands.common import build_by_authorization, group
from bissap.globals import json_output, json_print
from bissap.logging import get_logger
from bissap.roles import extract_role, get_role_description, get_roles_of_user

log = get_logger(__name__)


@group()
def roles():
    """List roles assigned to a user or with a specific authorization."""


@roles.command()
@click.argument('user')
def of_user(user: str):
    roles = get_roles_of_user(user)

    if json_output():
        json_print(roles)
    else:
        for role in roles:
            print(f'{role}: {get_role_description(role)}')


roles_by_auth = build_by_authorization(log, roles, extract_role)
