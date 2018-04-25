"""A utility to dump tiles directly from a local tiff file."""

from cogdumper.cog_tiles import AbstractReader


class Reader(AbstractReader):
    """Wraps the remote COG."""

    def __init__(self, handle):
        self._handle = handle

    def read(self, offset, length):
        self._handle.seek(offset)
        return self._handle.read(length)
