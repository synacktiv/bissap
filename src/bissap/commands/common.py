import sys
from logging import Logger
from typing import Callable

import click
from click import Group
from typing_extensions import override

from bissap.authorization import (
    RFC_NAME,
    RFC_TYPE,
    S_RFC,
    S_TCODE,
    TCD,
    AuthorizationField,
    AuthorizationObject,
)
from bissap.globals import json_output, json_print


class AliasedGroup(click.Group):
    @override
    def get_command(self, ctx, cmd_name):
        rv = super().get_command(ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return super().get_command(ctx, matches[0])
        ctx.fail(f'Too many matches: {", ".join(sorted(matches))}')

    @override
    def resolve_command(self, ctx, args):
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)
        if cmd is None:
            cmd_name = None
        else:
            cmd_name = cmd.name
        return cmd_name, cmd, args


def group(name: str | None = None, **kwargs):
    return click.group(name, **kwargs, cls=AliasedGroup)


def build_by_authorization(
    log: Logger, grp: Group, extract_func: Callable[[tuple[str, ...]], str]
):
    """
    Define a Click command to list users / profiles / whatever based on an authorization criteria.
    """

    @grp.command()
    @click.option('--objct', help='The authorization object (e.g. S_TCODE)')
    @click.option(
        '--field',
        '-f',
        'auth_fields',
        help='A list of fields to filter for. Format: FIELD:VALUE (e.g. TCD:SM16)',
        multiple=True,
    )
    @click.option(
        '--transaction', '-t', help='The transaction code to search for (e.g. SM16).'
    )
    @click.option(
        '--rfc', '-r', help='The name of the RFC to search for (e.g. RFCPING).'
    )
    @click.option('--rfc-type', help='The type of the RFC to search for (e.g. FUGR).')
    def by_authorization(
        objct: str | None,
        auth_fields: tuple[str, ...],
        transaction: str | None,
        rfc: str | None,
        rfc_type: str | None,
    ):
        """
        Filter by authorization value.

        Can specify a raw authorization value or a specific authorization object (e.g. Transaction, RFC, ...).
        """
        if objct is not None:
            assert transaction is None, (
                'Cannot specify manual fields and transaction at the same time.'
            )
            assert rfc is None, 'Cannot specify manual fields and RFC at the same time.'

            fields: set[AuthorizationField] = set()
            for f in auth_fields:
                try:
                    field, value = f.split(':')
                except ValueError:
                    log.error(
                        f'Invalid format for field {f}. Expected format: FIELD:VALUE (e.g. TCD:SM16)'
                    )
                    sys.exit(2)
                fields.add(AuthorizationField(field, value))

            auth_objct = AuthorizationObject(objct, frozenset(fields))
        elif transaction is not None:
            auth_objct = S_TCODE({TCD(transaction)})
        elif rfc is not None:
            fields = {RFC_NAME(rfc)}
            if rfc_type is not None:
                fields.add(RFC_TYPE(rfc_type))
            auth_objct = S_RFC(fields)
        else:
            log.error(
                'Missing a criteria. Please specify one of --objct / --transaction / --rfc'
            )
            sys.exit(2)

        users = auth_objct.all_users_with_authorization()
        specified_fields = set(map(extract_func, users))
        if json_output():
            json_print(specified_fields)
        else:
            for field in users:
                print(field)

    return by_authorization
