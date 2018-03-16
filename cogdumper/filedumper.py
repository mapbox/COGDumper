"""A utility to dump tiles directly from a local tiff file."""

import mimetypes

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
@click.option('--output', default=None, type=click.Path(exists=False, dir_okay=False, file_okay=False, writable=True), help='local output directory')
@click.option('--xyz', type=click.INT, default=[0, 0, 0], help='xyz tile coordinate where z is the overview level', nargs=3)
def dump(file, output, xyz=None):
    """Command line entry for COG tile dumping."""
    with open(file, 'rb') as src:
        reader = Reader(src)
        cog = COGTiff(reader.read)
        mime_type, tile = cog.get_tile(*xyz)
        if output is None:
            ext = mimetypes.guess_extension(mime_type)
            # work around a bug with mimetypes
            if ext == '.jpe':
                ext = '.jpg'
                
            output = f'file_{xyz[0]}_{xyz[1]}_{xyz[2]}{ext}'

        with open(output, 'wb') as dst:
            dst.write(tile)


if __name__ == "__main__":
    dump()
