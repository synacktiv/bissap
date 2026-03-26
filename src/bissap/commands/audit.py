import click

from bissap import logging
from bissap.auditing import (
    audit_all_roles,
    audit_all_users,
    audit_role,
    audit_roles_of_user,
    audit_user,
)
from bissap.roles import does_role_exist

log = logging.get_logger(__name__)


@click.command
@click.option(
    '--user', '-u', help='The user to audit. If omitted, will audit all users.'
)
@click.option('--role', '-r', help='If specified, audit a role instead of a user')
@click.option(
    '--roles',
    help='When auditing users, group results by roles',
    is_flag=True,
)
def audit(user: str | None, role: str | None, roles: bool):
    match (user, role, roles):
        case (None, None, False):
            audit_all_users()
        case (user, None, False):
            audit_user(user)
        case (None, None, True):
            audit_all_roles()
        case (user, None, True):
            audit_roles_of_user(user)
        case (None, role, False):
            if not does_role_exist(role):
                log.warning(f'Role {role} does not exists.')
            audit_role(role)
        case _:
            raise click.UsageError(
                'Invalid combination of argument. --user and --role are mutually exclusive. --roles cannot be specified if --role is used.'
            )
