"""A utility to dump tiles directly from a tiff file in an S3 bucket."""

import boto3
import click

from cogdumper.cog_tiles import (AbstractReader, COGTiff, print_version)


s3 = boto3.resource('s3')

class Reader(AbstractReader):
    """Wraps the remote COG."""
    def __init__(self, read_func, bucket_name, key):
        self.read_func = read_func
        self.bucket = bucket
        self.filename = key
        bucket = s3.Bucket(bucket_name)
        self.bucket_exists = True
        try:
            s3.meta.client.head_bucket(Bucket=bucket_name)
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                self.bucket_exists = False

    @property
    def bucket_exists(self):
        return self.bucket_exists

    def read(self, offset, length):
        pass


@click.command()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.option('--bucket', help='input bucket')
@click.option('--key', help='bucket key')
@click.option('--output', type=click.Path(exists=False, file_okay=False, writable=True), help='local output directory')
@click.option('--xyz', type=click.INT, default=None, help='xyz tile coordinates tile', nargs=3)
def dump(bucket, key, output, xyz=None):
    """Command line entry for COG tile dumping."""
    # copy the read function parameter from the libtiff library
    reader = Reader(bucket, key)
    cog = cog_tiles.COGTiff(reader.read)

    # either fetching one tile or dumping the lot
    if xyz:
        click.echo(f'xyz {xyz}')
    else:
        pass


if __name__ == "__main__":
    dump()
