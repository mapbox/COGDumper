"""A utility to dump tiles directly from a tiff file on a http server."""

import requests
from requests.auth import HTTPBasicAuth

from cogdumper.errors import TIFFError
from cogdumper.cog_tiles import AbstractReader


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
        start = offset
        stop = offset + length - 1
        headers = {'Range': f'bytes={start}-{stop}'}
        r = self.session.get(self.url, auth=self.auth, headers=headers)
        if r.status_code != requests.codes.partial_content:
            raise TIFFError(f'HTTP byte range {offset}-{length} '
                            'not available. HTTP code {r.status_code}')
        else:
            return r.content
