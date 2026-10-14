from typing import Literal

from bissap.auditing.exploit_paths import RCE_PATHS
from bissap.auditing.exploit_step import ExploitPath
from bissap.auditing.table import sensitive_tables_readable_by
from bissap.auditing.transaction import JUICY_TRANSACTIONS, Transaction
from bissap.globals import json_output, json_print
from bissap.logging import get_logger
from bissap.profiles import (
    get_profiles_of_role,
    get_profiles_of_user,
)
from bissap.roles import get_all_assigned_roles, get_roles_of_user
from bissap.users import all_users_name

log = get_logger(__name__)

# TODO: add exploitation path https://help.sap.com/docs/SAP_Solution_Manager/fd3c83ed48684640a18ac05c8ae4d016/4fa00d670cff44a5958237334a88af84.html?version=7.2.05


def _display_results(
    object_name: str,
    object_type: Literal['user', 'role'],
    exploitables_paths: list[ExploitPath],
    sensitive_tables: list[str],
    juicy_transactions: list[Transaction],
    brief: bool,
):
    if json_output():
        key = 'bname' if object_type == 'user' else 'role'
        json_print(
            {
                key: object_name,
                'rce': exploitables_paths,
                'tables': sensitive_tables,
                'transactions': juicy_transactions,
            }
        )
        return

    if len(exploitables_paths) > 0:
        if brief:
            details = f' ({", ".join([exp.name for exp in exploitables_paths])})'
        else:
            details = ''
        print(
            f'{object_name} is vulnerable to {len(exploitables_paths)} RCE(s).{details}'
        )
        if not brief:
            for exp in exploitables_paths:
                print(f'# {exp.name}')
                print(exp.description)
    else:
        if not brief:
            print(f'{object_name} is not vulnerable to any known RCE.')

    if len(sensitive_tables) > 0:
        print(f'{object_name} can read {len(sensitive_tables)} sensitive tables.')
        if not brief:
            for table in sensitive_tables:
                print(table)
    else:
        if not brief:
            print(f'{object_name} cannot read any known sensitive tables.')

    if len(juicy_transactions) > 0:
        if brief:
            details = f'({", ".join([tr.tcode for tr in juicy_transactions])})'
        else:
            details = ''
        print(
            f'{object_name} can execute {len(juicy_transactions)} "juicy" transactions. {details}'
        )
        if not brief:
            for tr in juicy_transactions:
                print(tr)
    else:
        if not brief:
            print(f'{object_name} cannot execute any "juicy" transaction.')


def _audit_profiles(
    object_name: str,
    object_type: Literal['user', 'role'],
    profiles: set[str],
    brief: bool,
):
    exploitables_paths = list(
        filter(lambda exp: exp.is_exploitable_by(profiles), RCE_PATHS)
    )
    sensitive_tables = list(sensitive_tables_readable_by(profiles))
    juicy_transactions = list(
        filter(lambda t: t.is_usable_by(profiles), JUICY_TRANSACTIONS)
    )

    _display_results(
        object_name,
        object_type,
        exploitables_paths,
        sensitive_tables,
        juicy_transactions,
        brief,
    )


def audit_user(bname: str, brief: bool = False):
    profiles = get_profiles_of_user(bname)
    _audit_profiles(bname, 'user', profiles, brief)


def audit_role(role_name: str, brief: bool = False):
    profiles = get_profiles_of_role(role_name)
    _audit_profiles(role_name, 'role', profiles, brief)


def audit_roles_of_user(bname: str):
    roles = get_roles_of_user(bname)
    for role in roles:
        audit_role(role, brief=True)


def audit_all_users():
    users = all_users_name()
    for user in users:
        audit_user(user, brief=True)


def audit_all_roles():
    roles = get_all_assigned_roles()

    for role in roles:
        audit_role(role, brief=True)
