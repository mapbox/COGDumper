"""cli."""

import mimetypes

import click

from cogdumper import __version__ as cogdumper_version
from cogdumper.cog_tiles import COGTiff
from cogdumper.s3dumper import Reader as S3Reader
from cogdumper.httpdumper import Reader as HTTPReader
from cogdumper.filedumper import Reader as FileReader


@click.group(short_help="Command line interface for COGDumper")
@click.version_option(version=cogdumper_version, message='%(version)s')
def cogdumper():
    """Command line interface for COGDumper."""
    pass


@cogdumper.command(help='COGDumper cli for AWS S3 hosted dataset')
@click.option('--bucket', required=True, help='AWS S3 bucket')
@click.option('--key', required=True, help='AWS S3 key')
@click.option('--output', default=None, type=click.Path(exists=False, file_okay=False, writable=True),
              help='local output directory')
@click.option('--xyz', type=click.INT, default=[0, 0, 0], nargs=3,
              help='xyz tile coordinates where z is the overview level')
def s3(bucket, key, output, xyz):
    """Read AWS S3 hosted dataset."""
    reader = S3Reader(bucket, key)
    cog = COGTiff(reader.read)
    mime_type, tile = cog.get_tile(*xyz)
    if output is None:
        ext = mimetypes.guess_extension(mime_type)
        # work around a bug with mimetypes
        if ext == '.jpe':
            ext = '.jpg'

        output = f's3_{xyz[0]}_{xyz[1]}_{xyz[2]}{ext}'

    with open(output, 'wb') as dst:
        dst.write(tile)


@cogdumper.command(help='COGDumper cli for web hosted dataset.')
@click.option('--server', required=True, help='server e.g. http://localhost:8080')
@click.option('--path', default=None, help='server path')
@click.option('--resource', help='server resource')
@click.option('--output', default=None, type=click.Path(exists=False, file_okay=False, writable=True),
              help='local output directory')
@click.option('--xyz', type=click.INT, default=[0, 0, 0], nargs=3,
              help='xyz tile coordinates where z is the overview level')
@click.version_option(version=cogdumper_version, message='%(version)s')
def http(server, path, resource, output, xyz=None):
    """Read web hosted dataset."""
    reader = HTTPReader(server, path, resource)
    cog = COGTiff(reader.read)
    mime_type, tile = cog.get_tile(*xyz)
    if output is None:
        ext = mimetypes.guess_extension(mime_type)
        # work around a bug with mimetypes
        if ext == '.jpe':
            ext = '.jpg'

        output = f'http_{xyz[0]}_{xyz[1]}_{xyz[2]}{ext}'

    with open(output, 'wb') as dst:
        dst.write(tile)


@cogdumper.command(help='COGDumper cli for local dataset.')
@click.option('--file', required=True, type=click.Path(exists=True, file_okay=True, dir_okay=False), help='input file')
@click.option('--output', default=None, type=click.Path(exists=False, dir_okay=False, file_okay=False, writable=True),
              help='local output directory')
@click.option('--xyz', type=click.INT, default=[0, 0, 0], nargs=3,
              help='xyz tile coordinate where z is the overview level')
@click.version_option(version=cogdumper_version, message='%(version)s')
def file(file, output, xyz=None):
    """Read local dataset."""
    with open(file, 'rb') as src:
        reader = FileReader(src)
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
