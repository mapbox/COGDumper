"""A utility to dump tiles directly from a local tiff file."""

import click

from cogdumper.cog_tiles import (AbstractReader, COGTiff, print_version)


class Reader(AbstractReader):
    """Wraps the remote COG."""
    def __init__(self, handle):
        self._handle = handle

    def read(self, offset, length):
        self._handle.seek(offset)
        return self._handle.read(length)


@click.command()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.option('--file', help='input file', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--output', type=click.Path(exists=False, dir_okay=True, file_okay=False, writable=True), help='local output directory')
@click.option('--xyz', type=click.INT, default=None, help='optional xyz tile coordinate where z is the overview level', nargs=3)
def dump(file, output, xyz=None):
    """Command line entry for COG tile dumping."""
    # copy the read function parameter from the libtiff library
    with open(file) as src:
        reader = Reader(src)
        cog = cog_tiles.COGTiff(reader.read)
        # either fetching one tile or dumping the lot
        if xyz:
            cog.get_tile(x, y, z)
        else:
            # TODO read all tiles
            pass


if __name__ == "__main__":
    dump()
