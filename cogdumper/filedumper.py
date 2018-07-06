"""A utility to dump tiles directly from a local tiff file."""

import logging
from cogdumper.cog_tiles import AbstractReader

logger = logging.getLogger(__name__)


class Reader(AbstractReader):
    """Wraps the remote COG."""

    def __init__(self, handle):
        self._handle = handle

    def read(self, offset, length):
        start = offset
        stop = offset + length - 1
        logger.info(f'Reading bytes: {start} to {stop}')
        self._handle.seek(offset)
        return self._handle.read(length)
