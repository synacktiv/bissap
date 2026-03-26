from pathlib import Path

import click

from bissap.commands.audit import audit
from bissap.commands.collect import collect
from bissap.commands.common import group
from bissap.commands.import_db import import_db
from bissap.commands.profiles import profiles
from bissap.commands.roles import roles
from bissap.commands.users import users
from bissap.db import init_database
from bissap.globals import set_client, set_json
from bissap.logging import init_logging

PRE_IMPORT_COMMANDS = {collect}
IMPORT_COMMAND = import_db


@group()
@click.option(
    '--client',
    '-m',
    help='The client / mandiant selected.',
)
@click.option(
    '--database',
    '-d',
    type=click.Path(readable=True, writable=True, path_type=Path),
)
@click.option('--json', is_flag=True, default=False)
@click.pass_context
def cli(ctx: click.Context, client: str | None, database: Path | None, json: bool):
    set_json(json)

    subcommand = ctx.invoked_subcommand

    is_pre_import = any(subcommand == cmd.name for cmd in PRE_IMPORT_COMMANDS)
    is_import = subcommand == IMPORT_COMMAND.name

    if is_pre_import:
        return

    if database is None:
        ctx.fail("Error: Missing option '--database' / '-d'.")
    init_database(database)

    if is_import:
        return

    if client is None:
        ctx.fail("Error: Missing option '--client' / '-m'.")
    set_client(client)


cli.add_command(audit)
cli.add_command(import_db)
cli.add_command(users)
cli.add_command(profiles)
cli.add_command(roles)
cli.add_command(collect)


def main():
    init_logging()
    cli()


if __name__ == '__main__':
    main()
