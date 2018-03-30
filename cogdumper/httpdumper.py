"""A utility to dump tiles directly from a tiff file on a http server."""

import mimetypes

import click
import requests
from requests.auth import HTTPBasicAuth

from cogdumper.errors import TIFFError

from cogdumper.cog_tiles import (AbstractReader, COGTiff, print_version)


class Reader(AbstractReader):
    """Wraps the remote COG."""
    def __init__(self, server, path, resource, user=None, password=None):
        self.server = server
        self.path = path
        self.resource = resource
        if path:
            self.url = f'{server}/{path}/{resource}'
        else:
            self.url = f'{server}/{resource}'
        if user:
            self.auth = HTTPBasicAuth(user, password)
        else:
            self.auth = None

        self._resource_exists = True

        self.session = requests.Session()
        r = self.session.head(self.url, auth=self.auth)
        if r.status_code != requests.codes.ok:
            self._resource_exists = False

    @property
    def resource_exists(self):
        return self._resource_exists

    def read(self, offset, length):
        headers = {'Range': f'bytes={offset}-{offset + length - 1}'}
        r = self.session.get(self.url, auth=self.auth, headers=headers)
        if r.status_code != requests.codes.partial_content:
            raise TIFFError(f'HTTP byte range {offset}-{length} '
                            'not available. HTTP code {r.status_code}')
        else:
            return r.content

@click.command()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.option('--server', help='server e.g. http://localhost:8080')
@click.option('--path', default=None, help='server path')
@click.option('--resource', help='server resource')
@click.option('--output', default=None, type=click.Path(exists=False, file_okay=False, writable=True), help='local output directory')
@click.option('--xyz', type=click.INT, default=[0, 0, 0], help='xyz tile coordinates where z is the overview level', nargs=3)
def dump(server, path, resource, output, xyz=None):
    """Command line entry for COG tile dumping."""
    reader = Reader(server, path, resource)
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



if __name__ == "__main__":
    dump()
