"""A utility to dump tiles directly from a tiff file on a http server."""

import requests
from requests.auth import HTTPBasicAuth

import click

from cogdumper.cog_tiles import (AbstractReader, COGTiff, print_version)


class Reader(AbstractReader):
    """Wraps the remote COG."""
    def __init__(self, server, path, resource, user=None, password=None):
        self.server = server
        self.path = path
        self.resource = resource
        self.url = f'{server}/{path}/{resource}'

        if user:
            self.auth = HTTPBasicAuth(user, password)
        else:
            self.auth = None

        self.resource_exists = True

        self.session = requests.Session()
        r = s.head(url, auth=self.auth)
        if r.status_code != requests.codes.ok:
            self.resource_exists = False

    @property
    def resource_exists(self):
        return self.resource_exists

    def read(self, offset, length):
        pass

@click.command()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.option('--server', help='server e.g. http://localhost:8080')
@click.option('--path', help='server path')
@click.option('--resource', help='server resource')
@click.option('--output', type=click.Path(exists=False, file_okay=False, writable=True), help='local output directory')
@click.option('--xyz', type=click.INT, default=None, help='xyz tile coordinates tile', nargs=3)
def dump(server, path, resource, output, xyz=None):
    """Command line entry for COG tile dumping."""
    # copy the read function parameter from the libtiff library
    reader = Reader(server, path, resource)
    cog = cog_tiles.COGTiff(reader.read)

    # either fetching one tile or dumping the lot
    if xyz:
        click.echo(f'xyz {xyz}')
    else:
        pass


if __name__ == "__main__":
    dump()
