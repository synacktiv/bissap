import logging
import os

from rich.console import Console
from rich.logging import RichHandler

LOGLEVEL = os.environ.get('LOG_LEVEL', 'WARNING').upper()


def init_logging():
    logging.basicConfig(
        level=LOGLEVEL, handlers=[RichHandler(console=Console(stderr=True))]
    )


def get_logger(name: str):
    logger = logging.getLogger(name)

    return logger
