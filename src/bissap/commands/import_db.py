from pathlib import Path

import click

from bissap.file_import import (
    import_from_csv,
    import_from_tsv,
    import_from_xlsx,
)


@click.command('import')
@click.option(
    '--input',
    '-i',
    type=click.Path(exists=True, path_type=Path),
    help='',
)
def import_db(input: Path):
    import_recursive(input)


def import_recursive(input: Path):
    if input.is_dir():
        for file in input.iterdir():
            import_recursive(file)
    else:
        import_file(input)


def import_file(input: Path):
    match input.suffix:
        case '.csv':
            import_from_csv(input)
        case '.xlsx':
            table_name = input.stem
            if table_name.startswith('EXPORT_'):
                click.echo(
                    f'Invalid filename ({input}). The filename must be the table name (e.g. USR02.xlsx)',
                    err=True,
                )
                return

            import_from_xlsx(input, table_name)
        case '.tsv':
            table_name = input.stem
            if table_name.startswith('EXPORT_'):
                click.echo(
                    f'Invalid filename ({input}). The filename must be the table name (e.g. USR02.xlsx)',
                    err=True,
                )
                return
            import_from_tsv(input, table_name)
        case _:
            click.echo(
                f'Unsupported extension {input.suffix}. Only .csv or .xlsx are supported.',
                err=True,
            )
            return
