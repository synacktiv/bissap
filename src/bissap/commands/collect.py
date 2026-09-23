from typing import Literal

import click
import sys

TABLES_TO_COLLECT = [
    'AGR_1016',
    'AGR_1016B',
    'AGR_1251',
    'AGR_DEFINE',
    'AGR_PROF',
    'AGR_TEXTS',
    'AGR_USERS',
    'DBCON',
    'RFCDES',
    'RSECTAB',
    'T000',
    'TDDAT',
    'TPFET',
    'TSTC',
    'USH02',
    'USOBHASH',
    'USR02',
    'USR10',
    'USR11',
    'USR12',
    'USR40',
    'USRPWDHISTORY',
    'UST04',
    'UST10C',
    'UST10S',
    'UST12',
]

SYBASE_SQL_CMD = '\n'.join(
    f'SELECT "{table}"\nSELECT * FROM {table}' for table in TABLES_TO_COLLECT
)

SYBASE_CMD = f"""isql -X -w9999999999 -s'|' -U$USER -P$PASSWORD -H$HOST -S$SYSTEM -o /tmp/dump_bissap.csv << EOF
SET NOCOUNT ON
{SYBASE_SQL_CMD}
GO
EOF"""

HANA_SQL_CMD = '\n'.join(
    f"SELECT '{table}' FROM DUMMY\nSELECT * FROM {table}" for table in TABLES_TO_COLLECT
)

HANA_CMD = f"""hdbsql -b all -F'|' -d$SYSTEM -n$HOST -u$USER -p$PASSWORD -o /tmp/dump_bissap.csv << EOF

{HANA_SQL_CMD}
EOF"""


@click.command()
@click.option('--type', '-t', 'type_', type=click.Choice(['hana', 'sybase', 'gui']))
def collect(type_: Literal['hana', 'sybase', 'gui']):
    if type_ == 'gui':
        click.echo(
            '1. Copy the directory `dump_table_autohotkey` to your workstation running SAP GUI'
        )
        click.echo(
            '2. Connect to the system and execute a supported transaction (SE16, DBACOCKPIT, ST04). If running DBACOCKPIT or ST04, go Diagnostics / SQL Command Line.'
        )
        click.echo(
            '3. Install AutoHotKey v2 (https://www.autohotkey.com/v2/) and execute the appropriate script.'
        )
        click.echo(
            '! Because the scripts relies on exact image recognition, the process can be brittle. For best results, run SAP GUI on a Windows VM, with a resolution of 1600 x 900 and SAP GUI with the default "Belize" theme'
        )
        click.echo(
            '! If the script fails, you can dump the tables manually using the list in `dump_table_autohotkey/tables.txt`.'
        )
        click.echo(
            '\nAt the end of the process, the result will be found in `Documents\\SAP\\SAP GUI`.'
        )
    else:
        click.echo(
            'Copy this command, set the appropriate environment variables (USER, PASSWORD, HOST and SYSTEM) and execute the command. Copy the file `/tmp/dump_bissap.csv` to your host.',
            err=True,
        )
        click.echo(
            f'Call {sys.argv[0]} -d DATABASE.sqlite import -i dump_bissap.csv to continue.',
            err=True,
        )
        match type_:
            case 'sybase':
                cmd = SYBASE_CMD
            case 'hana':
                cmd = HANA_CMD

        click.echo(
            cmd, nl=False
        )  # Do not put a newline at the end, so that when the output is directly copied, the command is not executed on paste.
        click.echo(err=True)
