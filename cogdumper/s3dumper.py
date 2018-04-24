"""A utility to dump tiles directly from a tiff file in an S3 bucket."""

import os

import boto3

from cogdumper.cog_tiles import AbstractReader

region = os.environ.get('AWS_REGION', 'us-east-1')
s3 = boto3.resource('s3', region_name=region)


class Reader(AbstractReader):
    """Wraps the remote COG."""

    def __init__(self, bucket_name, key):
        self.bucket = bucket_name
        self.key = key

    def read(self, offset, length):
        start = offset
        stop = offset + length - 1
        r = s3.meta.client.get_object(Bucket=self.bucket, Key=self.key,
                                      Range=f'bytes={start}-{stop}')
        return r['Body'].read()
