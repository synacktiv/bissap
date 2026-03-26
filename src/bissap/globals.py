import dataclasses
import json
from typing import Any

from typing_extensions import override

from bissap.db import does_table_exist, select_first
from bissap.logging import get_logger

log = get_logger(__name__)


class MyEncoder(json.JSONEncoder):
    @override
    def default(self, o):
        if isinstance(o, set | frozenset):
            return list(o)  # pyright: ignore[reportUnknownArgumentType]
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)  # pyright: ignore[reportArgumentType]
        return json.JSONEncoder.default(self, o)


_client = '000'


def set_client(client: str):
    global _client

    client_num = int(client)
    assert 0 <= client_num <= 999, (
        f'Invalid client number {client}. Must be an integer between 000 and 999'
    )

    _client = str(client_num).zfill(3)

    if does_table_exist('T000'):
        does_mandant_exist = (
            select_first('SELECT 1 FROM T000 WHERE MANDT = ?', (_client,)) is not None
        )
        if not does_mandant_exist:
            log.warning(f'Mandant {_client} does not exists.')


def client():
    return _client


_json = False


def set_json(json: bool):
    global _json
    _json = json


def json_output():
    return _json


def json_print(obj: Any):
    print(json.dumps(obj, cls=MyEncoder))
